import Worker from '$lib/utils/workers/FileProcessWorker.ts?worker';

export const processFile = async (
	files: File[],
	startFrom: number,
	previewRows: number = 5,
	startPreviewFrom: number = 0,
	{
		onPreview,
		onFull,
		onProgress,
		onError
	}: {
		onPreview: (data: { previewData: any[]; metadata: any }) => void;
		onFull: (data: { fileData: any[]; metadata: any }) => void;
		onProgress: (data: { message: string; percentage: number }) => void;
		onError: (data: { error: string }) => void;
	}
) => {
	if (!files?.[0]) return;
	const file = files[0];

	const worker = new Worker();
	worker.onmessage = (event: MessageEvent) => {
		const { type, ...data } = event.data;

		switch (type) {
			case 'preview':
				onPreview(data as { previewData: any[]; metadata: any });
				break;
			case 'full':
				onFull(data as { fileData: any[]; metadata: any });
				worker.terminate();
				break;
			case 'progress':
				onProgress(data as { message: string; percentage: number });
				break;
			case 'error':
				onError(data as { error: string });
				worker.terminate();
				break;
			default:
				console.warn('Unknown message type from worker:', type, data);
		}
	};

	worker.onerror = (error) => {
		console.error('Worker error:', error);
		onError({ error: `Помилка Web Worker: ${error.message || 'Невідома помилка'}` });
	};

	try {
		const fileBuffer = await file.arrayBuffer();
		worker.postMessage({
			fileBuffer,
			fileName: file.name,
			startFrom,
			previewRowsCount: previewRows,
			startPreviewFrom
		});
	} catch (error: any) {
		console.error('Error reading file:', error);
		onError({ error: `Помилка читання файлу: ${error.message || 'Невідома помилка'}` });
	}
};
