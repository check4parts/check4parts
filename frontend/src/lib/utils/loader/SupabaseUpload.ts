// src/lib/utils/supabaseUploadManager.ts
import Worker from '$lib/utils/workers/SupabaseUploadWorker.ts?worker';
import { parseJwt } from './ParseJWT';
import type { TransformedItem } from './TransformFile.svelte';

export type AppSettings = {
	startFrom: number;
	chunkSize: number;
	concurrencyLimit: number;
};

export type WorkerMessage =
	| {
			type: 'startUpload';
			data: {
				data: TransformedItem[];
				providerId: string;
				settings: AppSettings;
				authToken: string;
				hash: string;
				loadedId?: string | null;
				currency: string;
				companyId: string;
				supabaseAnonKey: string;
				supabaseUrl: string;
			};
	  }
	| {
			type: 'progress';
			payload: { uploadedCount: number; totalCount: number; percentage: number; message: string };
	  }
	| { type: 'complete'; payload: { totalCount: number } }
	| {
			type: 'error';
			payload: {
				message: string;
				uploadedCount?: number;
				totalCount?: number;
				percentage?: number;
			};
	  };

export type PriceRowForDB = {
	brand: string;
	article: string;
	price: number | null;
	description: string | null;
	provider_id: string;
	rests: any;
	loaded_id: string;
};

let uploadWorker: Worker | null = null;
let currentOnProgress:
	| ((progress: {
			uploadedCount: number;
			totalCount: number;
			percentage: number;
			message: string;
	  }) => void)
	| undefined;
let currentReject: ((reason?: any) => void) | undefined;

export async function startWorkerUpload(
	data: TransformedItem[],
	hash: string,
	currency: string,
	loadedId: string | null,
	providerId: string,
	authToken: string,
	supabaseUrl: string,
	supabaseAnonKey: string,
	onProgress?: (progress: {
		uploadedCount: number;
		totalCount: number;
		percentage: number;
		message: string;
	}) => void,
	settings: AppSettings = {
		startFrom: 0,
		chunkSize: 5000,
		concurrencyLimit: 4
	}
): Promise<void> {
	return new Promise((resolve, reject) => {
		// Terminate existing worker if any, to ensure a clean slate
		if (uploadWorker) {
			uploadWorker.terminate();
			uploadWorker = null;
		}

		const companyId = parseJwt(authToken).company_id; // Replace with actual company ID or pass it as a parameter

		uploadWorker = new Worker();

		currentOnProgress = onProgress;
		currentReject = reject; // Store reject for error handling

		uploadWorker.onmessage = (event: MessageEvent<WorkerMessage>) => {
			const { type } = event.data;
			const payload = (event.data as any).payload; // Safely extract payload if it exists
			switch (type) {
				case 'progress':
					if (payload) {
						currentOnProgress?.(payload);
					}
					break;
				case 'complete':
					currentOnProgress?.({
						uploadedCount: payload?.totalCount || 0,
						totalCount: payload?.totalCount || 0,
						percentage: 100,
						message: 'Завантаження завершено!'
					});
					uploadWorker?.terminate();
					uploadWorker = null;
					resolve();
					break;
				case 'error':
					currentOnProgress?.({
						uploadedCount: payload?.uploadedCount || 0,
						totalCount: payload?.totalCount || 0,
						percentage: payload?.percentage || 0,
						message: `Помилка: ${payload?.message || 'Unknown error'}`
					});
					uploadWorker?.terminate();
					uploadWorker = null;
					reject(new Error(payload?.message || 'Unknown error'));
					break;
			}
		};

		uploadWorker.onerror = (error: ErrorEvent) => {
			console.error('Worker error:', error);
			currentOnProgress?.({
				uploadedCount: 0,
				totalCount: 0,
				percentage: 0,
				message: `Критична помилка воркера: ${error.message}`
			});
			uploadWorker?.terminate();
			uploadWorker = null;
			reject(new Error(`Критична помилка воркера: ${error.message}`));
		};

		// Get Supabase URL and Key from the client instance (assuming it was created using PUBLIC env vars)
		// You might need a more robust way to get these if your client setup is different.

		// Send the data and configuration to the worker
		uploadWorker.postMessage({
			type: 'startUpload',
			data: {
				data: data,
				providerId,
				settings: settings,
				authToken,
				supabaseUrl,
				supabaseAnonKey,
				hash,
				loadedId,
				companyId,
				currency
			}
		});
	});
}

export function terminateWorkerUpload() {
	if (uploadWorker) {
		uploadWorker.terminate();
		uploadWorker = null;
		currentOnProgress?.({
			uploadedCount: 0,
			totalCount: 0,
			percentage: 0,
			message: 'Завантаження скасовано.'
		});
		currentReject?.(new Error('Upload cancelled by user.'));
	}
}
