<script lang="ts">
	import { PUBLIC_SUPABASE_PRICES_ANON_KEY, PUBLIC_SUPABASE_PRICES_URL } from '$env/static/public';
	import InputSelect from '$lib/components/inputs/modal/InputSelect.svelte';
	import { autoMapHeaders } from '$lib/utils/loader/AutoMap';
	import { parseJwt } from '$lib/utils/loader/ParseJWT.js';
	import { processFile } from '$lib/utils/loader/ProcessFile.js';
	import {
		startWorkerUpload,
		terminateWorkerUpload,
		type AppSettings
	} from '$lib/utils/loader/SupabaseUpload.js';
	import {
		StartTransformFileWorker,
		type TransformedItem,
		type MappedHeader
	} from '$lib/utils/loader/TransformFile.svelte.js';

	let { data } = $props();
	let { providers, warehouses } = $derived(data);

	let company_id = $derived<string>(parseJwt(data.session?.access_token || '')?.company_id || '');

	let selected_provider = $state<string>('');
	let files: FileList | null = $state(null);
	let fileLoading = $state(false);
	let transformingData = $state(false);

	let uploadingToDB = $state(false);
	let uploadedToDB = $state(false);
	let uploadDBMessage = $state('');
	let uploadDBPercentage = $state(0);
	let uploadedTotalCount = $state(0);

	let settings: AppSettings = $state<AppSettings>({
		startFrom: 2,
		chunkSize: 3000,
		concurrencyLimit: 3
	});
	let settingsCollapsed = $state(true);

	let previewData: any[] = $state([]);
	let fullFileData: any[] = $state.raw([]);
	let transformedData: TransformedItem[] = $state.raw([]);
	let fileTransformed = $state(false);
	let hashFullTransformedData = $state('');
	let loadedId: string | null = $state(null);
	let processingMessage = $state('');
	let processingPercentage = $state(0);
	let errorMessage = $state('');

	let fileHeaders: string[] = $state([]);
	let firstRowHeaders: string[] = $state([]);
	let mappedHeaders: MappedHeader[] = $state([]);

	let currentProviderWarehouses = $derived(
		warehouses.filter((warehouse) => warehouse.provider_id === selected_provider)
	);

	// Нова змінна стану для зберігання промісу перевірки хешу
	let hashCheckPromise: Promise<{ loaded_id: string | null; hashExists: any[] }> | null =
		$state(null);

	$effect(() => {
		mappedHeaders = autoMapHeaders(firstRowHeaders, currentProviderWarehouses);
	});

	$inspect(mappedHeaders);
	function toggleSettingsCollapse() {
		settingsCollapsed = !settingsCollapsed;
	}

	async function checkHashExists(hash: string) {
		// 1. Знаходимо loaded_id по hash
		let { data: loaded_prices, error } = await data.supabasePrices
  		.from('loaded_prices')
  		.select('id')
			.eq('hash', hash)
			.single()

		console.log('Loaded ID:', loaded_prices?.id);
		loadedId = loaded_prices?.id || null;
		if (!loadedId) {
			return {
				loaded_id: null,
				hashExists: []
			};
		}

		// 2. Знаходимо всі price_history з цим loaded_id
		const { data: priceData } = await data.supabasePrices
			.from('price_history')
			.select('id', { count: 'exact' })
			.eq('loaded_id', loadedId);
		console.log('Hash Check Data:', priceData);
		return {
			loaded_id: loadedId || null,
			hashExists: priceData || []
		};
	}

	async function handleFileUpload(event: Event) {
		event.preventDefault();
		uploadedToDB = false;

		if (!files || files.length === 0) {
			errorMessage = 'Будь ласка, оберіть файл для завантаження.';
			return;
		}

		if (!selected_provider) {
			errorMessage = 'Будь ласка, оберіть провайдера.';
			return;
		}

		resetStatesForNewUpload();

		await processFile(files, settings.startFrom - 1, 5, 0, {
			onPreview: ({ previewData: data, metadata }) => {
				console.log('Preview Data:', data);
				previewData = data;
				fileHeaders = metadata.headers;
				firstRowHeaders = Object.values(data[0]);
			},
			onFull: ({ fileData: data }) => {
				fullFileData = data;
				fileLoading = false;
				processingMessage = 'Обробка файлу завершена. Будь ласка, зіставте колонки.';
				processingPercentage = 100;
			},
			onProgress: ({ message, percentage }) => {
				console.log('Progress:', message, percentage);
				processingMessage = message;
				processingPercentage = percentage;
			},
			onError: ({ error }) => {
				console.error('Error from worker:', error);
				errorMessage = error;
				fileLoading = false;
				processingMessage = 'Помилка обробки файлу.';
				processingPercentage = 0;
				resetErrorStates();
			}
		});
	}

	async function handleTransformData() {
		transformingData = true;
		errorMessage = '';
		processingMessage = 'Підготовка до трансформації даних...';
		processingPercentage = 0;

		try {
			// Викликаємо функцію StartTransformFileWorker, глибоко клонуючи fullFileData, щоб уникнути DataCloneError
			const result = await StartTransformFileWorker(
				fullFileData, // Глибоке клонування даних
				$state.snapshot(mappedHeaders), // Глибоке клонування mappedHeaders,
				selected_provider,
				company_id,
				data.session?.access_token || '', // Передаємо authToken
				({ state }) => {
					if (state === 'transforming') {
						processingMessage = 'Трансформація даних...';
					} else if (state === 'hash') {
						processingMessage = 'Обрахування хешу...';
					}
					processingPercentage += 20; // Збільшуємо відсоток для візуалізації прогресу
				}
			);

			transformedData = result.transformedData;
			hashFullTransformedData = result.hash;

			processingMessage = 'Дані успішно трансформовані! Тепер можете завантажити їх в базу даних.';
			fileTransformed = true;
			// Запускаємо початкову перевірку хешу після трансформації
			hashCheckPromise = checkHashExists(hashFullTransformedData);
		} catch (error: any) {
			console.error('Error during data transformation:', error);
			errorMessage = `Помилка трансформації даних: ${error.message || 'Невідома помилка'}`;
			processingMessage = 'Помилка трансформації даних.';
		} finally {
			transformingData = false;
			processingPercentage = 100;
		}
	}

	async function handleUploadToDatabase() {
		uploadingToDB = true;

		if (!selected_provider) {
			errorMessage = 'Будь ласка, оберіть провайдера перед завантаженням в базу даних.';
			return;
		}

		errorMessage = '';
		uploadDBMessage = 'Завантаження даних до бази даних...';
		uploadDBPercentage = 0;

		try {
			uploadedToDB = false;
			await startWorkerUpload(
				transformedData,
				$state.snapshot(hashFullTransformedData),
				loadedId,
				selected_provider,
				$state.snapshot(settings),
				data.session?.access_token || '',
				PUBLIC_SUPABASE_PRICES_URL,
				PUBLIC_SUPABASE_PRICES_ANON_KEY,
				({
					uploadedCount,
					totalCount,
					percentage,
					message
				}: {
					uploadedCount: number;
					totalCount: number;
					percentage: number;
					message: string;
				}) => {
					uploadDBMessage = message;
					uploadDBPercentage = percentage;
					uploadedTotalCount = uploadedCount;
				}
			);
			uploadDBMessage = 'Дані успішно завантажено в базу даних!';
			uploadedToDB = true;
			// Повторно запускаємо перевірку хешу після успішного завантаження
			hashCheckPromise = checkHashExists(hashFullTransformedData);
		} catch (error: any) {
			console.error('Error uploading to database:', error);
			errorMessage = `Помилка завантаження до бази даних: ${error.message || 'Невідома помилка'}`;
			uploadDBMessage = 'Помилка завантаження до бази даних.';
		} finally {
			uploadingToDB = false;
		}
	}

	function getColumnDisplayName(index: string, table: boolean = false): string {
		const parsedIndex = parseInt(index, 10);
		if (!isNaN(parsedIndex)) {
			return table ? `${parsedIndex + 1}` : `Колонка ${parsedIndex + 1}`;
		}
		return index;
	}

	function resetStatesForNewUpload() {
		fileLoading = true;
		errorMessage = '';
		processingMessage = '';
		processingPercentage = 0;
		previewData = [];
		fullFileData = [];
		fileHeaders = [];
		firstRowHeaders = [];
		transformingData = false;
		fileTransformed = false;
		uploadingToDB = false;
		uploadDBMessage = '';
		uploadDBPercentage = 0;
		uploadedToDB = false; // Скидаємо цей стан також
		hashCheckPromise = null; // Скидаємо проміс перевірки хешу
		terminateWorkerUpload();
	}

	function resetErrorStates() {
		transformingData = false;
		fileTransformed = false;
		uploadingToDB = false;
		uploadDBMessage = '';
		uploadDBPercentage = 0;
	}
</script>

<section class="bg-surface-50 my-5 w-full rounded-lg p-5">
	<h3 class="mb-4 flex items-center justify-between text-xl font-semibold text-gray-800">
		Налаштування
		<button
			class="rounded-full p-1 transition-all duration-200 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
			onclick={toggleSettingsCollapse}
			aria-expanded={!settingsCollapsed}
			aria-label={settingsCollapsed ? 'Розгорнути налаштування' : 'Згорнути налаштування'}
		>
			<svg
				class="h-5 w-5 text-gray-600 transition-transform duration-300"
				class:rotate-180={!settingsCollapsed}
				xmlns="http://www.w3.org/2000/svg"
				fill="none"
				viewBox="0 0 24 24"
				stroke="currentColor"
			>
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"
				></path>
			</svg>
		</button>
	</h3>
	{#if !settingsCollapsed}
		<div class="grid grid-cols-1 gap-4 transition-all duration-300 ease-out md:grid-cols-2">
			<div class="flex flex-col">
				<label for="startFromInput" class="mb-1 block text-sm font-medium text-gray-700"
					>Почати обробку з рядка</label
				>
				<input
					id="startFromInput"
					type="number"
					min="1"
					bind:value={settings.startFrom}
					placeholder="Наприклад, 2"
					required
					class="block w-full rounded-lg border border-gray-300 px-4 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:bg-gray-100 disabled:text-gray-500"
				/>
				<p class="mt-1 text-sm text-gray-500">
					Вкажіть номер рядка, з якого почнеться обробка даних у файлі.
				</p>
			</div>

			<div class="flex flex-col">
				<label for="chunkSizeInput" class="mb-1 block text-sm font-medium text-gray-700"
					>Розмір чанка</label
				>
				<input
					id="chunkSizeInput"
					type="number"
					min="1"
					bind:value={settings.chunkSize}
					required
					class="block w-full rounded-lg border border-gray-300 px-4 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:bg-gray-100 disabled:text-gray-500"
				/>
				<p class="mt-1 text-sm text-gray-500">
					Вкажіть максимальну кількість рядків для обробки в одному чанку. Більші чанки швидші, але
					вимагають більше пам'яті.
				</p>
			</div>

			<div class="flex flex-col">
				<label for="concurrencyLimitInput" class="mb-1 block text-sm font-medium text-gray-700"
					>Паралельні завантаження</label
				>
				<input
					id="concurrencyLimitInput"
					type="number"
					min="1"
					bind:value={settings.concurrencyLimit}
					required
					class="block w-full rounded-lg border border-gray-300 px-4 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:bg-gray-100 disabled:text-gray-500"
				/>
				<p class="mt-1 text-sm text-gray-500">
					Визначте кількість чанків, які будуть завантажуватися паралельно. Більше паралельних
					завантажень може пришвидшити процес, але збільшує навантаження на базу даних.
				</p>
			</div>
		</div>
	{/if}
</section>

<section class="bg-surface-50 w-full rounded-lg p-5">
	<form
		aria-label="Завантаження файлу та вибір провайдера"
		class="mx-auto flex flex-row justify-between gap-4"
		onsubmit={handleFileUpload}
	>
		<label for="fileInput" class="w-full">
			<span class="label">Оберіть файл для завантаження</span>
			<input
				id="fileInput"
				class="focus:border-primary-500 mt-1 h-12 w-full rounded-md bg-white px-3 py-2 text-sm placeholder:text-gray-400 focus:outline-none"
				type="file"
				accept=".xlsx,.xls,.csv,.txt"
				bind:files
				required
			/>
		</label>
		<InputSelect
			items={providers.map((provider) => ({
				label: provider.name,
				value: provider.id
			}))}
			bind:value={selected_provider}
			label="Оберіть провайдера"
			placeholder="Виберіть зі списку"
			name="provider-select"
			required
		/>

		<button
			class="btn preset-filled-primary-950-50"
			type="submit"
			disabled={fileLoading || !files || files.length === 0 || !selected_provider}
			aria-busy={fileLoading}
		>
			{#if fileLoading}
				Обробка...
			{:else}
				Завантажити файл
			{/if}
		</button>
	</form>

	{#if errorMessage}
		<p class="mt-4 text-red-600">{errorMessage}</p>
	{/if}

	{#if processingMessage}
		<div class="mt-4">
			<p class="text-sm text-gray-700">{processingMessage}</p>
			<div class="mt-2 h-2.5 w-full rounded-full bg-gray-200">
				<div class="h-2.5 rounded-full bg-blue-600" style="width: {processingPercentage}%"></div>
			</div>
		</div>
	{/if}

	{#if previewData.length > 0}
		<div class="mt-4">
			<div>
				<div class="flex h-9 gap-4">
					<div class="badge preset-filled-primary-50-950 text-md">
						<i class="fas fa-file"></i> Розмір: {files ? (files[0].size / 1024).toFixed(2) : '0.00'}
						KB
					</div>
					<div class="badge preset-filled-primary-50-950 text-md">
						<i class="fas fa-list"></i> Рядків: {fullFileData.length}
					</div>
					<div class="badge preset-filled-primary-50-950 text-md">
						<i class="fas fa-calendar"></i> Дата: {files
							? new Date(files[0].lastModified).toLocaleDateString('uk')
							: 'N/A'}
					</div>
					{#if fileTransformed}
						<div class="badge preset-filled-primary-50-950 text-md">
							<i class="fas fa-fingerprint"></i> Хеш: {hashFullTransformedData.slice(0, 8)}
						</div>
						{#if hashCheckPromise}
							{#await hashCheckPromise then data}
								{#if loadedId}
									<div class="badge preset-filled-success-50-950 text-md">
										<i class="fas fa-check"></i> Файл вже є
									</div>
								{/if}
								{#if data.hashExists.length === 0}
									<div class="badge preset-filled-success-50-950 text-md">
										<i class="fas fa-check"></i> Хеш не існує
									</div>
								{:else}
									<a
										href="/home/prices/{data.hashExists[0].id}"
										target="_blank"
										class="badge preset-filled-error-50-950 text-md hover:bg-red-100"
									>
										<i class="fas fa-times"></i> Хеш існує
									</a>
								{/if}
								<div class="text-center">
									<button
										class="btn preset-filled-primary-950-50"
										onclick={handleUploadToDatabase}
										disabled={uploadingToDB || !selected_provider || data.hashExists.length > 0}
										aria-busy={uploadingToDB}
									>
										{#if uploadingToDB}
											Завантаження в БД...
										{:else}
											{data.hashExists.length > 0
												? 'Таки файл ви вже завантажували'
												: 'Завантажити в БД'}
										{/if}
									</button>
								</div>
							{:catch error}
								<div class="badge preset-filled-primary-50-950 text-md">
									<i class="fas fa-exclamation-triangle"></i> Помилка перевірки хешу: {error.message}
								</div>
							{/await}
						{/if}
					{/if}
				</div>
			</div>
		</div>

		{#if uploadingToDB}
			<div class="mt-4">
				<p class="text-sm text-gray-700">{uploadDBMessage}</p>
				<div class="mt-2 h-2.5 w-full rounded-full bg-gray-200">
					<div class="h-2.5 rounded-full bg-green-600" style="width: {uploadDBPercentage}%"></div>
				</div>
			</div>
		{/if}

		{#if uploadedToDB}
			<div class="mt-4">
				<p class="text-sm text-green-600">Дані успішно завантажено в базу даних!</p>
				<p class="text-sm text-gray-500">
					Завантажено {uploadedTotalCount} записів для провайдера {providers.find(
						(p) => p.id === selected_provider
					)?.name || selected_provider}.
				</p>
			</div>
		{/if}

		<!-- {#if !fileTransformed} -->
		<div class="mt-4 overflow-x-auto">
			<table class="min-w-full divide-y divide-gray-200 overflow-hidden rounded-lg shadow-sm">
				<thead class="bg-gray-50">
					<tr>
						{#each fileHeaders as fileHeader}
							<th
								scope="col"
								class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500"
							>
								{getColumnDisplayName(fileHeader, true)}
							</th>
						{/each}
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-200 bg-white">
					{#each previewData as row}
						<tr>
							{#each fileHeaders as fileHeader}
								<td class="whitespace-nowrap px-6 py-4 text-sm text-gray-900">
									{row[fileHeader]}
								</td>
							{/each}
						</tr>
					{/each}
				</tbody>
			</table>
		</div>

		<div class="mt-8">
			<h4 class="mb-3 text-lg font-semibold text-gray-800">
				Зіставлення колонок та попередній перегляд:
			</h4>

			<div class="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2">
				{#each mappedHeaders as headerMap, index (headerMap.value)}
					<div class="flex flex-col">
						<label for="map-{headerMap.value}" class="mb-1 block text-sm font-medium text-gray-700">
							{headerMap.name} ({headerMap.type === 'prop' ? 'Властивість' : 'Залишки'})
						</label>
						<select
							id="map-{headerMap.value}"
							bind:value={mappedHeaders[index].header}
							class="block w-full rounded-lg border border-gray-300 px-4 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
						>
							<option value="">Не обрано</option>
							{#each fileHeaders as fileHeader}
								<option value={fileHeader}>{getColumnDisplayName(fileHeader)}</option>
							{/each}
						</select>
						{#if headerMap.header === ''}
							<p class="mt-1 text-xs text-red-500">
								Цей заголовок не знайдено автоматично. Будь ласка, оберіть вручну.
							</p>
						{/if}
					</div>
				{/each}
			</div>
			<p class="text-sm text-gray-500">
				Ви можете змінити зіставлення колонок, щоб відповідати вашому файлу. Після завершення
				зіставлення, натисніть "Завершити зіставлення" для обробки даних.
			</p>
			<button
				class="btn preset-filled-primary-950-50 mt-4"
				onclick={handleTransformData}
				disabled={transformingData || fileLoading}
				aria-busy={transformingData}
			>
				{#if transformingData}
					Трансформація...
				{:else}
					Завершити зіставлення
				{/if}
			</button>
		</div>
	{/if}
	<!-- {/if} -->

	{#if fileTransformed && fullFileData.length > 0}
		<div class="mt-8">
			<h4 class="mb-3 text-lg font-semibold text-gray-800">
				Трансформовані дані (перші 5 записів):
			</h4>
			<div class="overflow-x-auto">
				<table class="min-w-full divide-y divide-gray-200 overflow-hidden rounded-lg shadow-sm">
					<thead class="bg-gray-50">
						<tr>
							<th
								scope="col"
								class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500"
								>Бренд</th
							>
							<th
								scope="col"
								class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500"
								>Код Бренду</th
							>
							<th
								scope="col"
								class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500"
								>Ціна</th
							>
							<th
								scope="col"
								class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500"
								>Опис</th
							>
							<th
								scope="col"
								class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500"
								>Залишки (Склади)</th
							>
						</tr>
					</thead>
					<tbody class="divide-y divide-gray-200 bg-white">
						{#each (transformedData as TransformedItem[]).slice(0, 5) as item}
							<tr>
								<td class="whitespace-nowrap px-6 py-4 text-sm text-gray-900">{item.brand}</td>
								<td class="whitespace-nowrap px-6 py-4 text-sm text-gray-900">{item.article}</td>
								<td class="whitespace-nowrap px-6 py-4 text-sm text-gray-900">{item.price}</td>
								<td class="whitespace-nowrap px-6 py-4 text-sm text-gray-900">{item.description}</td
								>
								<td class="whitespace-nowrap px-6 py-4 text-sm text-gray-900">
									{#each Object.entries(item.rests) as [warehouseId, count]}
										<div>
											{currentProviderWarehouses.find((wh) => wh.id === warehouseId)?.name ||
												warehouseId}: {count}
										</div>
									{/each}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
			{#if fullFileData.length > 5}
				<p class="mt-2 text-sm text-gray-600">
					...та ще {transformedData.length - 5} рядків. ({fullFileData.length - 5})
				</p>
			{/if}
		</div>
	{/if}
</section>
