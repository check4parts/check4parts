import type { MappedHeader, TransformedItem, WorkerMessage } from '../loader/TransformFile.svelte';

async function transformFileData(
	fileData: any[],
	mappedHeaders: MappedHeader[],
	selectedProvider: string
): Promise<TransformedItem[]> {
	const transformedData: TransformedItem[] = [];

	const propMappings = new Map<string, string>();
	const restMappings = new Map<string, string>();

	mappedHeaders.forEach((mh) => {
		if (mh.header !== '') {
			if (mh.type === 'prop') {
				propMappings.set(mh.value, String(mh.header));
			} else if (mh.type === 'rests') {
				restMappings.set(mh.value, String(mh.header));
			}
		}
	});

	// Yield control to the event loop to prevent blocking the worker thread for large files.
	await new Promise((resolve) => setTimeout(resolve, 0));

	for (const row of fileData) {
		const newItem: TransformedItem = {
			brand: '',
			article: '',
			price: 0,
			description: '',
			provider_id: selectedProvider,
			rests: {}
		};

		newItem.article = String(row[propMappings.get('article') ?? ''] || '');
		if (newItem.article === '') {
			continue;
		}

		newItem.brand = String(row[propMappings.get('brand') ?? ''] || '');
		newItem.description = String(row[propMappings.get('description') ?? ''] || '');

		const priceStr = String(row[propMappings.get('price') ?? ''] || '').replace(',', '.');
		newItem.price = parseFloat(priceStr) || 0;

		for (const [warehouseId, fileColumnIndex] of restMappings.entries()) {
			const restValue = String(row[fileColumnIndex] || '');
			newItem.rests[warehouseId] = restValue || 0;
		}

		transformedData.push(newItem);
	}

	return transformedData;
}

async function calculateHashForTransformedData(
	transformedData: TransformedItem[],
	companyId: string
): Promise<string> {
	// Ensure CryptoJS is loaded and available.
	const CryptoJS = (await import('crypto-js')).default;
	if (transformedData.length > 500000) {
		console.warn('Transformed data is too large for hash calculation');
		return CryptoJS.SHA256(
			JSON.stringify(new Date().getTime().toPrecision(12)) + companyId
		).toString(CryptoJS.enc.Hex);
	}
	return CryptoJS.SHA256(JSON.stringify(transformedData)).toString(CryptoJS.enc.Hex);
}

function postMessageToMain(message: WorkerMessage) {
	self.postMessage(message);
}

self.onmessage = async (event: MessageEvent<WorkerMessage>) => {
	const { type } = event.data;
	const data = (event.data as { data?: any }).data;

	if (type === 'startUpload') {
		try {
			const { data: fileData, mappedHeaders, providerId, companyId } = data;
			console.log('Starting file transformation in worker', {
				fileData,
				mappedHeaders,
				providerId,
				companyId
			});

			// Notify main thread about transformation progress
			postMessageToMain({ type: 'progress', payload: { state: 'transforming' } });
			const transformedData = await transformFileData(fileData, mappedHeaders, providerId);

			// Notify main thread about hash calculation progress
			postMessageToMain({ type: 'progress', payload: { state: 'hash' } });
			const hash = await calculateHashForTransformedData(transformedData, companyId);
			// Notify main thread about completion
			postMessageToMain({ type: 'complete', payload: { transformedData, hash } });
		} catch (error: any) {
			// Notify main thread about any errors
			postMessageToMain({
				type: 'error',
				payload: { message: error.message || 'An unknown error occurred during processing.' }
			});
		}
	}
};
