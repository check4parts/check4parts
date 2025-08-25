import Worker from '$lib/utils/workers/TransfromFileWorker.ts?worker';
import type { Template } from './AutoMap';

export type MappedHeader = {
	name: string;
	value: string;
	type: string;
	header: string;
	aliases?: string[];
};

export interface TransformedItem {
	brand: string;
	article: string;
	price: number;
	description: string;
	provider_id: string;
	rests: {
		[warehouseId: string]: number | string;
	};
	[key: string]: any;
}

export type WorkerMessage =
	| {
			type: 'startUpload';
			data: {
				data: any[];
				mappedHeaders: MappedHeader[];
				providerId: string;
				companyId: string;
				authToken: string;
			};
	  }
	| { type: 'progress'; payload: { state: 'transforming' | 'hash' } }
	| { type: 'complete'; payload: { transformedData: TransformedItem[]; hash: string } }
	| { type: 'error'; payload: { message: string } };

export async function checkHashExists(
	hash: string,
	supabasePrices: any
): Promise<{ loaded_id: string | null; hashExists: any[] }> {
	let { data: loaded_prices, error } = await supabasePrices
		.from('loaded_prices')
		.select('id')
		.eq('hash', hash)
		.single();

	let loadedId = loaded_prices?.id || null;
	if (!loadedId) {
		return {
			loaded_id: null,
			hashExists: []
		};
	}

	// 2. Знаходимо всі price_history з цим loaded_id
	const { data: priceData, error: priceError } = await supabasePrices
		.from('price_history')
		.select('id', { count: 'exact' })
		.eq('loaded_id', loadedId);
	return {
		loaded_id: loadedId || null,
		hashExists: priceData || []
	};
}

export function transformPreviewData(
	data: any[],
	template: Template,
	selectedProvider: string
): TransformedItem[] {
	return data
		.map((row) => {
			const transformedRow: TransformedItem = {
				brand: '',
				article: '',
				price: 0,
				description: '',
				provider_id: selectedProvider,
				rests: {}
			};

			template.template.forEach((templateRow) => {
				if (templateRow.type === 'prop') {
					const value = row[templateRow.header] || '';
					switch (templateRow.value) {
						case 'article':
							transformedRow.article = String(value);
							break;
						case 'brand':
							transformedRow.brand = String(value);
							break;
						case 'description':
							transformedRow.description = String(value);
							break;
						case 'price':
							transformedRow.price = parseFloat(String(value).replace(',', '.')) || -1;
							break;
					}
				} else if (templateRow.type === 'rests') {
					const warehouseId = templateRow.value;
					if (templateRow.header) {
						const restValue = row[templateRow.header] || 0;
						transformedRow.rests[warehouseId] = restValue;
					} else {
						transformedRow.rests[warehouseId] = 'Невідомо';
					}
				}
			});
			return transformedRow.article && transformedRow.price !== -1 ? transformedRow : null;
		})
		.filter((item): item is TransformedItem => item !== null);
}

export async function StartTransformFileWorker(
	fileData: any[],
	mappedHeaders: MappedHeader[],
	providerId: string,
	companyId: string,
	authToken: string,
	onProgress: (progress: { state: 'transforming' | 'hash' }) => void
): Promise<{ transformedData: TransformedItem[]; hash: string }> {
	return new Promise((resolve, reject) => {
		const worker = new Worker();

		worker.onmessage = (event: MessageEvent<WorkerMessage>) => {
			const message = event.data;

			switch (message.type) {
				case 'progress':
					onProgress(message.payload);
					break;
				case 'complete':
					worker.terminate(); // Завершити воркер після завершення роботи
					resolve(message.payload);
					break;
				case 'error':
					console.error('Помилка воркера:', message.payload.message);
					worker.terminate(); // Завершити воркер у випадку помилки
					reject(new Error(message.payload.message));
					break;
				default:
					console.warn('Отримано невідоме повідомлення від воркера:', message);
			}
		};

		// Обробник помилок воркера
		worker.onerror = (error: ErrorEvent) => {
			console.error('Загальна помилка воркера:', error);
			worker.terminate();
			reject(new Error(`Помилка веб-воркера: ${error.message}`));
		};

		// Відправка початкового повідомлення воркеру для запуску трансформації
		worker.postMessage({
			type: 'startUpload',
			data: {
				data: fileData,
				mappedHeaders: mappedHeaders,
				providerId: providerId,
				companyId: companyId,
				authToken: authToken
			}
		} as WorkerMessage);
	});
}
