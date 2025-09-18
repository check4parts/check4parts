// src/lib/utils/workers/SupabaseUploadWorker.ts
import { createClient, type SupabaseClient } from '@supabase/supabase-js';
import type { WorkerMessage, PriceRowForDB } from '$lib/utils/loader/SupabaseUpload';

// === Константи (не змінюємо публічний API) ===
const MAX_REQUESTS_PER_SECOND = 10;
const MAX_CHUNK_SIZE = 5000;
const MAX_RETRIES = 3;

// === Допоміжні утиліти ===
function sleep(ms: number) {
	return new Promise((res) => setTimeout(res, ms));
}

function isRetryable(error: any) {
	const code = error?.code ?? error?.status ?? 0;
	return code === 0 || code === 429 || (code >= 500 && code <= 599);
}

const SLOT_MS = Math.ceil(1000 / MAX_REQUESTS_PER_SECOND);
let lastStart = 0;
let tokens = MAX_REQUESTS_PER_SECOND;
const refill = setInterval(() => (tokens = MAX_REQUESTS_PER_SECOND), 1000);

async function scheduleStart() {
	const now = Date.now();
	const wait = Math.max(0, lastStart + SLOT_MS - now);
	if (wait) await sleep(wait);
	lastStart = Date.now();

	while (tokens <= 0) {
		await sleep(20);
	}
	tokens--;
}

let lastProgressTs = 0;
function postProgressThrottled(uploadedCount: number, totalCount: number, message: string) {
	const now = Date.now();
	// не частіше ~1 разу на 120мс
	if (now - lastProgressTs < 120) return;
	lastProgressTs = now;
	const percentage = Math.max(0, Math.min(100, Math.round((uploadedCount / totalCount) * 100)));

	self.postMessage({
		type: 'progress',
		payload: { uploadedCount, totalCount, percentage, message }
	} satisfies WorkerMessage);
}

async function ensureLoadedId(
	supabase: SupabaseClient,
	loadedId: string | null,
	hash: string
): Promise<string> {
	if (loadedId) return loadedId;

	// idempotent upsert по унікальному hash
	const { data, error } = await supabase
		.from('loaded_prices')
		.upsert({ hash }, { onConflict: 'hash' })
		.select('id')
		.single();

	if (error) throw new Error(`Не вдалося отримати/створити loaded_id: ${error.message}`);
	return data!.id as string;
}

async function createHistory(
	supabase: SupabaseClient,
	providerId: string,
	loadedId: string,
	status: 'uploading' | 'cloned',
	currency: string
): Promise<{ id: string; created_at: string }> {
	const { data, error } = await supabase
		.from('price_history')
		.insert({ provider_id: providerId, status, loaded_id: loadedId, currency })
		.select('id, created_at')
		.single();

	if (error) throw new Error(`Не вдалося створити price_history: ${error.message}`);
	return data as { id: string; created_at: string };
}

async function setHistoryStatus(
  supabase: SupabaseClient,
  historyId: string,
  status: 'actual' | 'failed'
) {
  const updates: Record<string, any> = { status };
  if (status === 'failed') {
    updates.loaded_id = null;
  }

  const { error } = await supabase
    .from('price_history')
    .update(updates)
    .eq('id', historyId);

  if (error) {
    console.warn(`Помилка оновлення статусу історії (${historyId}): ${error.message}`);
  }
}

async function deleteOldPrices(
	supabase: SupabaseClient,
	providerId: string,
	historyCreatedAt: string
) {

	const { error } = await supabase
		.from('price_history')
		.update({ status: 'deleted', loaded_id: null })
		.eq('provider_id', providerId)
		.neq('status', 'deleted')
		.lt('created_at', historyCreatedAt);

	if (error) {
		console.warn('Помилка масового видалення старих записів:', error.message);
	}
}


function makeRangeGetter(total: number, startFrom: number, size: number) {
	let start = Math.max(0, startFrom);
	const max = total;
	return function next(): [number, number] | null {
		if (start >= max) return null;
		const s = start;
		const e = Math.min(max, start + size);
		start = e;
		return [s, e];
	};
}

function mapRows(
	data: any[],
	start: number,
	end: number,
	providerId: string,
	loadedId: string
): PriceRowForDB[] {
	const out = new Array<PriceRowForDB>(end - start);
	for (let i = start, j = 0; i < end; i++, j++) {
		const it = data[i];
		out[j] = {
			brand: it.brand,
			article: it.article,
			price: it.price ?? null,
			description: it.description ? String(it.description) : null,
			provider_id: providerId,
			rests: it.rests,
			loaded_id: loadedId
		};
	}
	return out;
}

async function insertWithRetry(
	supabase: SupabaseClient,
	rows: PriceRowForDB[],
	maxRetries = MAX_RETRIES
) {
	let attempt = 0;
	while (true) {
		await scheduleStart();
		const { error } = await supabase.from('prices').insert(rows);
		if (!error) return;

		if (!isRetryable(error) || attempt >= maxRetries) {
			const msg = error?.message || 'Insert failed';
			throw new Error(msg);
		}
		attempt++;
		const base = 200 * Math.pow(2, attempt - 1);
		const jitter = Math.random() * 120;
		await sleep(base + jitter);
	}
}

// === Основний обробник повідомлень ===
self.onmessage = async (event: MessageEvent<WorkerMessage>) => {
	if (event.data.type !== 'startUpload') return;

	const {
		data,
		providerId,
		settings,
		authToken,
		hash,
		loadedId: maybeLoadedId,
		supabaseUrl,
		supabaseAnonKey,
		currency
	} = event.data.data;

	const supabase = createClient(supabaseUrl, supabaseAnonKey, {
		global: { headers: { Authorization: `Bearer ${authToken}` } }
	});

	try {
		// 1) гарантуємо loaded_id
		const loadedId = await ensureLoadedId(supabase, maybeLoadedId ?? null, hash);

		// 2) створення history
		if (maybeLoadedId) {
			// сценарій cloning: не вантажимо заново, просто робимо історію
			const hist = await createHistory(supabase, providerId, loadedId, 'cloned', currency);
			await deleteOldPrices(supabase, providerId, hist.created_at);
			self.postMessage({ type: 'complete', payload: { totalCount: 0 } });
			return;
		}

		const history = await createHistory(supabase, providerId, loadedId, 'uploading', currency);

		const totalCount = data.length;
		let uploadedCount = 0;

		// 3) підготовка чанків
		const CHUNK = Math.max(1, Math.min(settings?.chunkSize ?? MAX_CHUNK_SIZE, MAX_CHUNK_SIZE));
		const CONC = Math.max(1, settings?.concurrencyLimit ?? 5);
		const startFrom = Math.max(0, settings?.startFrom ?? 0);

		const nextRange = makeRangeGetter(totalCount, startFrom, CHUNK);

		// 4) паралельні "воркери" з обмеженням по CONC
		let dynamicChunkSize = CHUNK;
		async function runner() {
			while (true) {
				const range = nextRange();
				if (!range) return;
				const [s, e] = range;

				let rows = mapRows(data, s, e, providerId, loadedId);

				try {
					await insertWithRetry(supabase, rows);
					uploadedCount += rows.length;
					postProgressThrottled(
						uploadedCount,
						totalCount,
						`Завантажено ${uploadedCount}/${totalCount}`
					);
				} catch (err: any) {
					const msg = String(err?.message ?? '');
					if (msg.includes('413') && e - s > 1) {
						// зменшимо чанк удвічі
						dynamicChunkSize = Math.max(1, Math.floor(dynamicChunkSize / 2));
						// перестворимо діапазони дрібніше: повернемо частину назад у "ітератор"
						// оскільки ми не зберігаємо глобальну чергу, просто локально доробимо цей блок дрібнішими шматками
						for (let i = s; i < e; i += dynamicChunkSize) {
							const ss = i;
							const ee = Math.min(e, i + dynamicChunkSize);
							const subRows = mapRows(data, ss, ee, providerId, loadedId);
							await insertWithRetry(supabase, subRows); // тут теж працює rate-limit + retry
							uploadedCount += subRows.length;
							postProgressThrottled(
								uploadedCount,
								totalCount,
								`Завантажено ${uploadedCount}/${totalCount}`
							);
						}
					} else {
						throw err;
					}
				}
			}
		}

		const workers: Promise<void>[] = [];
		for (let i = 0; i < CONC; i++) workers.push(runner());

		try {
			await Promise.all(workers);
			await setHistoryStatus(supabase, history.id, 'actual');
			await deleteOldPrices(supabase, providerId, history.created_at);
			self.postMessage({ type: 'complete', payload: { totalCount } });
		} catch (e: any) {
			await setHistoryStatus(supabase, history.id, 'failed');
			const percentage = totalCount ? Math.round((uploadedCount / totalCount) * 100) : 0;
			self.postMessage({
				type: 'error',
				payload: {
					message: e?.message || 'Upload failed',
					uploadedCount,
					totalCount,
					percentage
				}
			} as WorkerMessage);
		}
	} catch (fatal: any) {
		// помилка на ранній стадії (loaded_id/history)
		self.postMessage({
			type: 'error',
			payload: {
				message: fatal?.message || 'Fatal error',
				uploadedCount: 0,
				totalCount: 0,
				percentage: 0
			}
		} as WorkerMessage);
	} finally {
		clearInterval(refill);
	}
};
