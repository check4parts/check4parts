// src/lib/utils/supabaseUploadWorker.ts
import { createClient, type SupabaseClient } from '@supabase/supabase-js';
import type { AppSettings, PriceRowForDB, WorkerMessage } from '../loader/SupabaseUpload';
import type { TransformedItem } from '../loader/TransformFile.svelte';

function postMessageToMain(message: WorkerMessage) {
	self.postMessage(message);
}

async function deleteOldPrices(supabase: SupabaseClient, providerId: string, historyCreatedAt: string) {
	const { data, error } = await supabase
		.from('price_history')
		.select('*')
		.eq('provider_id', providerId)
		.neq('status', 'deleted')
		.lt('created_at', historyCreatedAt)

	console.log('Old price history data to delete:', data);
	if (data) {
		for (const item of data) {
			console.log(`Deleting old price history (${item.id})...`);
			const { error } = await supabase
				.from('price_history')
				.update({ status: 'deleted', loaded_id: null })
				.eq('id', item.id)
			console.log(`Deleted old price history (${item.id}):`);
			if (error) {
				console.error(`Error deleting old price history (${item.id}):`, error.message);
			}
		}
	}

}

async function uploadPricesToSupabaseInWorker(
	data: TransformedItem[],
	hash: string,
	loadedId: string | null,
	providerId: string,
	settings: AppSettings,
	supabase: SupabaseClient,
	companyId: string
): Promise<void> {
	const totalCount = data.length;
	let uploadedCount = 0;
	const chunkSize = settings.chunkSize;
	const concurrencyLimit = settings.concurrencyLimit || 5;
	let historyId: string | null = null;
	let historyCreatedAt: string | null = null;

	try {
		if (loadedId) {
			postMessageToMain({
				type: 'progress',
				payload: {
					uploadedCount: 0,
					totalCount,
					percentage: 0,
					message: 'Знайдено існуючий запис прайсу, даємо доступ...'
				}
			});

			const { data: historyData, error: historyError } = await supabase
				.from('price_history')
				.insert({
					provider_id: providerId,
					status: 'cloned',
					loaded_id: loadedId,
				})
				.select('id, created_at')
				.single();

			console.log('History data:', historyData);
			historyId = historyData!.id;
			historyCreatedAt = historyData!.created_at;

			if (historyError) {
				throw new Error(
					`Помилка створення історії цін: ${historyError.message}, ${JSON.stringify(historyError)}, ${providerId}`
				);
			}

		} else {

			postMessageToMain({
				type: 'progress',
				payload: {
					uploadedCount: 0,
					totalCount,
					percentage: 0,
					message: 'Створення запису історії завантаження...'
				}
			});
			const { data: loadedData, error: loadedError } = await supabase
				.from('loaded_prices')
				.insert({
					hash: hash,
				})
				.select('id')
				.single();

			if (loadedError) {
				throw new Error(
					`Помилка створення історії цін: ${loadedError.message}, ${JSON.stringify(loadedError)}, ${providerId}`
				);
			}
			const newLoadedId = loadedData.id;

			const { data: historyData, error: historyError } = await supabase
				.from('price_history')
				.insert({
					provider_id: providerId,
					status: 'uploading',
					loaded_id: newLoadedId,
				})
				.select('id, created_at')
				.single();

			if (historyError) {
				throw new Error(
					`Помилка створення історії цін: ${historyError.message}, ${JSON.stringify(historyError)}, ${providerId}`
				);
			}
			historyId = historyData.id;
			historyCreatedAt = historyData.created_at;

			postMessageToMain({
				type: 'progress',
				payload: {
					uploadedCount: 0,
					totalCount,
					percentage: 5,
					message: 'Початок завантаження даних...'
				}
			});

			// Create an array of promises, limiting concurrency
			const allChunkPromises: Promise<void>[] = [];
			for (let i = 0; i < totalCount; i += chunkSize) {
				const chunkToProcess = data.slice(i, i + chunkSize);
				if (chunkToProcess.length > 0) {
					allChunkPromises.push(
						(async (currentChunk, currentChunkIndex) => {
							// Wrap in an IIFE to capture chunk context
							const rowsToInsert: PriceRowForDB[] = currentChunk.map((item) => ({
								brand: item.brand,
								article: item.article,
								price: item.price,
								description: item.description === '' ? null : item.description,
								provider_id: providerId,
								rests: item.rests,
								loaded_id: newLoadedId,
							}));

							try {
								const { error } = await supabase.from('prices').insert(rowsToInsert);
								if (error) {
									const { error: updateError } = await supabase
										.from('price_history')
										.update({ status: 'failed' })
										.eq('id', historyId);
									if (updateError) {
										console.warn(
											`Помилка оновлення статусу історії цін (${historyId}): ${updateError.message}`
										);
									}
									throw new Error(
										`Помилка завантаження даних (пакет ${Math.floor(currentChunkIndex / chunkSize) + 1}): ${JSON.stringify(error)}`
									);
								}
								// Atomically update uploadedCount and send progress
								uploadedCount += currentChunk.length;
								const percentage = Math.min(95, (uploadedCount / totalCount) * 90 + 5);
								postMessageToMain({
									type: 'progress',
									payload: {
										uploadedCount,
										totalCount,
										percentage,
										message: `Завантаження... ${uploadedCount} з ${totalCount} записів.`
									}
								});
							} catch (e: any) {
								console.error('Error during chunk upload:', e);
								throw e; // Re-throw to be caught by Promise.all
							}
						})(chunkToProcess, i) // Pass chunk and its starting index
					);
				}
			}

			// Use a queue to manage concurrency
			const uploadQueue = async (tasks: Promise<void>[], limit: number) => {
				const results = [];
				const running: Promise<void>[] = [];

				for (const task of tasks) {
					if (running.length >= limit) {
						await Promise.race(running);
					}
					const p = task.then((res) => {
						running.splice(running.indexOf(p), 1);
						return res;
					});
					running.push(p);
					results.push(p);
				}
				return Promise.all(results);
			};

			await uploadQueue(allChunkPromises, concurrencyLimit);

			// 3. Update price_history status to 'actual'
			if (historyId) {
				postMessageToMain({
					type: 'progress',
					payload: {
						uploadedCount: totalCount,
						totalCount,
						percentage: 95,
						message: 'Завершення завантаження...'
					}
				});
				const { error: updateError } = await supabase
					.from('price_history')
					.update({ status: 'actual' })
					.eq('id', historyId);
				if (updateError) {
					console.warn(
						`Помилка оновлення статусу історії цін (${historyId}): ${updateError.message}`
					);
				}
			}

		}
		await deleteOldPrices(supabase, providerId, historyCreatedAt!);

		postMessageToMain({ type: 'complete', payload: { totalCount } });
	} catch (error: any) {
		console.error('Upload process failed in worker:', error);
		// Ensure history status is updated to 'failed' on error
		if (historyId) {
			await supabase.from('price_history').update({ status: 'failed' }).eq('id', historyId);
		}
		postMessageToMain({
			type: 'error',
			payload: {
				message: error.message,
				uploadedCount,
				totalCount,
				percentage: Math.min(95, (uploadedCount / totalCount) * 90 + 5)
			}
		});
	}
}

// Listen for messages from the main thread
self.onmessage = (event: MessageEvent<WorkerMessage>) => {
	if (event.data.type === 'startUpload') {
		const { data, providerId, settings, authToken, hash, loadedId, companyId } = event.data.data;

		uploadPricesToSupabaseInWorker(
			data,
			hash,
			loadedId ? loadedId : null,
			providerId,
			settings,
			createClient(event.data.data.supabaseUrl, event.data.data.supabaseAnonKey, {
				global: {
					headers: {
						Authorization: `Bearer ${authToken}`
					}
				}
			}),
			companyId,
		);
	}
};
