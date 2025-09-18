<script lang="ts">
	import { FileUpload } from '@skeletonlabs/skeleton-svelte';
	import StepsBar from './(components)/StepsBar.svelte';
	import { parseJwt } from '$lib/utils/loader/ParseJWT';
	import { processFile } from '$lib/utils/loader/ProcessFile.js';
	import InputSelect from '$lib/components/inputs/modal/InputSelect.svelte';
	import TemplateModal from './(components)/TemplateModal.svelte';
	import { autoMapHeaders, type Template } from '$lib/utils/loader/AutoMap';
	import {
		checkHashExists,
		StartTransformFileWorker,
		transformPreviewData,
		type TransformedItem
	} from '$lib/utils/loader/TransformFile.svelte';
	import { startWorkerUpload, terminateWorkerUpload } from '$lib/utils/loader/SupabaseUpload';
	import { PUBLIC_SUPABASE_PRICES_ANON_KEY, PUBLIC_SUPABASE_PRICES_URL } from '$env/static/public';

	let { data } = $props();
	let { providers, warehouses, currencies, providerTemplates } = $derived(data);

	let company_id = $derived<string>(parseJwt(data.session?.access_token || '')?.company_id || '');

	let selected_provider = $state<string>('');
	let selected_currency = $state<string>('');

	let currentProviderWarehouses = $derived(
		warehouses.filter((warehouse) => warehouse.provider_id === selected_provider)
	);
	let curentProviderTemplate = $derived(
		providerTemplates?.find((t: any) => t.provider_id === selected_provider)
	);

	let step = $state<number>(1);
	let stepState = $state<'current' | 'error' | 'success'>('current');


	let uploadedFiles = $state<File[]>([]);
	let fileLoading = $state(false);

	let uploadingToDB = $state(false);
	let uploadedToDB = $state(false);
	let uploadDBMessage = $state('');
	let uploadDBPercentage = $state(0);
	let uploadedCount = $state(0);
	let totalCount = $state(0);

	let previewData: any[] = $state([]);
	let fileHeaders: string[] = $state([]);
	let firstRowHeaders: string[] = $state([]);
	let fullFileData: any[] = $state.raw([]);
	let processingMessage = $state('');
	let processingPercentage = $state(0);
	let errorMessage = $state('');

	let templateModalOpenState = $state(false);
	let template = $state<Template>({ metadata: { firstRowHeaders: true }, template: [] });
	let previewTransformedData = $derived(
		transformPreviewData(previewData, template, selected_provider)
	);
	let templateComleated = $derived(
		template.template.filter((row) => row.type === 'prop').every((row) => row.header !== '') &&
			!!selected_provider
	);
	let transformingData = $state(false);
	let transformedData: TransformedItem[] = $state.raw([]);
	let fileTransformed = $state(false);
	let hashCheck = $state<{ loaded_id: string | null; hashExists: any[] }>({
		loaded_id: null,
		hashExists: []
	});
	let hashFullTransformedData: string = $state('');

	$effect(() => {
		if (previewData.length > 0) {
			template.template = autoMapHeaders(
				Object.values(previewData[0]),
				currentProviderWarehouses,
				curentProviderTemplate?.template
			);
		}
	});

	$effect(() => {
		if (step) {
			stepState = 'current';
			processingMessage = '';
			processingPercentage = 0;
		}
	});

	$effect(() => {
		template.metadata.providerId = selected_provider;
	});

	function getHeaderLabel(header: string, index: number): string {
		if (header) {
			return isNaN(parseInt(header)) ? header : `Колонка №${parseInt(header) + 1}`;
		}
		return `Колонка №${index + 1}`;
	}

	let headersLabels = $derived<string[]>(
		(template.metadata.firstRowHeaders ? Object.values(previewData[0] ?? []) : fileHeaders).map(
			(header, index) => getHeaderLabel(header as string, index)
		)
	);

	async function handleFileUpload() {
		uploadedToDB = false;

		await processFile(uploadedFiles, 1, 5, 0, {
			onPreview: ({ previewData: data, metadata }) => {
				previewData = data;
				fileHeaders = metadata.headers;
			},
			onFull: ({ fileData: data }) => {
				fullFileData = data;
				fileLoading = false;
				processingMessage = 'Обробка файлу завершена.';
				processingPercentage = 100;
			},
			onProgress: ({ message, percentage }) => {
				processingMessage = message;
				processingPercentage = percentage;
			},
			onError: ({ error }) => {
				console.error('Error from worker:', error);
				errorMessage = error;
				fileLoading = false;
				processingMessage = 'Помилка обробки файлу.';
				processingPercentage = 0;
			}
		});
	}

	async function handleTransformData() {
		transformingData = true;
		errorMessage = '';
		processingMessage = 'Підготовка до трансформації даних...';
		processingPercentage = 0;

		try {
			const result = await StartTransformFileWorker(
				$state.snapshot(fullFileData),
				$state.snapshot(template.template),
				selected_provider,
				company_id,
				data.session?.access_token || '',
				({ state }) => {
					if (state === 'transforming') {
						processingMessage = 'Трансформація даних...';
					} else if (state === 'hash') {
						processingMessage = 'Обрахування хешу...';
					}
					processingPercentage += 20;
				}
			);

			transformedData = result.transformedData;
			hashFullTransformedData = result.hash;

			processingMessage = 'Дані успішно трансформовані! Тепер можете завантажити їх в базу даних.';
			fileTransformed = true;
			hashCheck = await checkHashExists(hashFullTransformedData, data.supabasePrices);
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
				selected_currency,
				hashCheck.loaded_id,
				selected_provider,
				data.session?.access_token || '',
				PUBLIC_SUPABASE_PRICES_URL,
				PUBLIC_SUPABASE_PRICES_ANON_KEY,
				({
					uploadedCount: uploaded,
					totalCount: total,
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
					uploadedCount = uploaded;
					totalCount = total;
				}
			);
			uploadDBMessage = 'Дані успішно завантажено в базу даних!';
			uploadedToDB = true;
		} catch (error: any) {
			console.error('Error uploading to database:', error);
			errorMessage = `Помилка завантаження до бази даних: ${error.message || 'Невідома помилка'}`;
			uploadDBMessage = 'Помилка завантаження до бази даних.';
		} finally {
			uploadingToDB = false;
		}
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
		selected_provider = '';
		uploadingToDB = false;
		uploadDBMessage = '';
		uploadDBPercentage = 0;
		uploadedToDB = false; // Скидаємо цей стан також
		hashCheck = { loaded_id: null, hashExists: [] }; // Скидаємо проміс перевірки хешу
		terminateWorkerUpload();
	}

	function formatFileSize(bytes: number, decimals = 2) {
		if (bytes === 0) return '0 Bytes';

		const k = 1000;
		const dm = decimals < 0 ? 0 : decimals;
		const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

		const i = Math.floor(Math.log(bytes) / Math.log(k));

		return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
	}
</script>

<TemplateModal
	bind:openState={templateModalOpenState}
	modalClose={() => (templateModalOpenState = false)}
	data={{
		previewData,
		fileHeaders,
		headersLabels
	}}
	bind:template
	supabase={data.supabasePrices}
/>
<main class="flex h-full w-full flex-col gap-4">
	<header>
		<h1 class="h4">Завантаження цін постачальників</h1>
		<div class="mt-10 flex items-center justify-center">
			<StepsBar bind:step {stepState} />
		</div>
	</header>

	<section class="overflow-y-auto">
		{#if step === 1}
			<h2 class="h5 top-0 flex items-center gap-2 bg-white">
				<img src="/step-1.svg" alt="Крок 1" /> Крок 1: Завантажте файл з цінами
			</h2>
			<form
				aria-label="Завантаження файлу та вибір провайдера"
				onsubmit={(e) => {
					e.preventDefault();
					handleFileUpload();
				}}
			>
				<FileUpload
					name="priceFile"
					accept=".xlsx,.xls,.csv,.txt"
					maxFiles={1}
					onFileChange={(e) => {
						const files = e.acceptedFiles;
						resetStatesForNewUpload();
						if (files.length > 0) {
							uploadedFiles = files;
						} else {
							stepState = 'error';
						}
					}}
					classes="w-full"
					label="Виберіть файл"
				>
					{#snippet iconInterface()}<img src="/upload-icon.svg" alt="upload" />{/snippet}
					{#snippet iconFile()}<img src="/step-1.svg" alt="File" />{/snippet}
				</FileUpload>
				{#if !fullFileData.length}
					{#if uploadedFiles.length}
						<div class="mt-4 flex w-full gap-2">
							<button
								class="btn preset-filled-primary-950-50"
								type="submit"
								aria-busy={fileLoading}
							>
								Завантажити файл
							</button>
							{#if processingMessage}
								<div class="w-full">
									<p class="text-sm text-gray-700">{processingMessage}</p>
									<div class="h-2.5 w-full rounded-full bg-gray-200">
										<div
											class="h-2.5 rounded-full bg-blue-600"
											style="width: {processingPercentage}%"
										></div>
									</div>
								</div>
							{/if}
						</div>
					{/if}
				{:else}
					<p class="card preset-tonal-success mt-4 w-full p-4 text-center">
						Дані успішно оброблено. Ви можете перейти до наступного кроку для перевірки даних.
					</p>
					<div class="flex justify-end">
						<button
							class="btn preset-filled-primary-950-50 mt-4"
							onclick={() => {
								step = 2;
							}}
						>
							Далі
						</button>
					</div>
				{/if}
			</form>
		{:else if step === 2}
			<h2 class="h5 flex">
				<img src="/step-2.svg" alt="Крок 2" /> Крок 2: Перевірте дані
			</h2>
			<section class="mt-4" id="settings">
				<div>
					<div>
						<p class="text-md font-bold text-gray-700">Виберіть постачальника:</p>
						<div class="z-50 w-full rounded-lg border-2 border-gray-200 bg-white">
							<InputSelect
								placeholder="Виберіть зі списку"
								name="provider"
								items={providers.map((provider) => ({
									label: provider.name,
									value: provider.id
								}))}
								required
								bind:value={selected_provider}
								intialValue={selected_provider}
							/>
						</div>
						<div>
							<p class="text-md font-bold text-gray-700">Виберіть валюту:</p>
							<div class="z-50 w-full rounded-lg border-2 border-gray-200 bg-white">
								<InputSelect
									placeholder="Виберіть зі списку"
									name="currency"
									items={currencies.map((currency) => ({
										label: `${currency.name} (${currency.code})`,
										value: currency.id
									}))}
									required
									bind:value={selected_currency}
									intialValue={selected_currency}
								/>
							</div>
						</div>
					</div>
				</div>
			</section>
			<section class="mt-4" id="basic-info">
				<div class="flex items-center justify-between">
					<div class="flex h-9 gap-4">
						<div class="badge preset-filled-surface-100-900 text-md">
							<i class="fas fa-file"></i>
							Розмір: {uploadedFiles.length > 0 ? formatFileSize(uploadedFiles[0].size) : '0 B'}
						</div>
						<div class="badge preset-filled-surface-100-900 text-md">
							<i class="fas fa-list"></i> Рядків: {fullFileData.length}
						</div>
						<div class="badge preset-filled-surface-100-900 text-md">
							<i class="fas fa-calendar"></i> Дата: {uploadedFiles.length > 0
								? new Date(uploadedFiles[0].lastModified).toLocaleDateString('uk')
								: 'N/A'}
						</div>
					</div>
					<div>
						<button
							class="btn preset-filled-primary-100-900 font-bold"
							onclick={() => {
								templateModalOpenState = true;
							}}
							aria-label="Налаштування колонок"
						>
							<i class="fas fa-gear"></i> Налаштування колонок
						</button>
					</div>
				</div>
			</section>
			<section class="mt-4" id="dataPreview">
				<h3 class="h5">Попередній перегляд:</h3>
				{#if previewData.length > 0}
					<div class="border-primary-950 overflow-hidden rounded-xl border-2">
						<div class="max-h-[70vh] overflow-y-auto">
							<table class="table min-w-full table-auto border-collapse">
								<thead class="bg-primary-950 sticky top-0">
									<tr class="text-primary-50">
										{#each headersLabels as header}
											<th class="px-4 py-2 text-left">{header}</th>
										{/each}
									</tr>
								</thead>
								<tbody class="!divide-primary-950 !divide-y-2">
									{#each template.metadata.firstRowHeaders ? previewData.slice(1) : previewData as row}
										<tr class="hover:bg-primary-50 group w-full divide-x-2">
											{#each Object.values(row) as cell}
												<td class="whitespace-nowrap px-4 py-2">{cell}</td>
											{/each}
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
					</div>
				{/if}
			</section>
			{#if previewTransformedData.length > 0}
				<section class="mt-4">
					<h3 class="h5">Співставлені дані:</h3>
					<div class="border-primary-950 overflow-hidden rounded-xl border-2">
						<div class="max-h-[70vh] overflow-y-auto">
							<table class="table min-w-full table-auto border-collapse">
								<thead class="bg-primary-950 sticky top-0">
									<tr class="text-primary-50">
										{#each template.template as col}
											<th class="px-4 py-2 text-left">{col.name}</th>
										{/each}
									</tr>
								</thead>
								<tbody class="!divide-primary-950 !divide-y-2">
									{#each previewTransformedData as row}
										<tr class="hover:bg-primary-50 group w-full divide-x-2">
											{#each template.template as col}
												<td class="px-4 py-2 text-sm">
													{#if col.type === 'rests'}
														{row.rests?.[col.value] || 0}
													{:else}
														{row[col.value] || ''}
													{/if}
												</td>
											{/each}
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
					</div>
				</section>
			{:else}
				<p class="text-gray-700">Співставлені дані будуть відображені тут після налаштування колонок.</p>
			{/if}
			<section class="mt-4">
				{#if templateComleated}
					<div class="flex w-full gap-4">
						<button
							class="btn preset-filled-primary-950-50"
							onclick={() => {
								step = 3;
								handleTransformData();
							}}
						>
							Далі
						</button>
					</div>
					{#if errorMessage}
						<p class="text-error-500">{errorMessage}</p>
					{/if}
				{:else}
					<p class="text-error-500">
						Будь ласка, налаштуйте всі колонки перед переходом до наступного кроку.
					</p>
				{/if}
			</section>
		{:else if step === 3}
			<header>
				<h2 class="h5 flex items-center gap-2">
					<img src="/step-3.svg" alt="Крок 3" /> Крок 3: Завантажте дані в базу
				</h2>
			</header>
			<section class="mt-4">
				<div class="flex h-8 items-center justify-start gap-4">
					<button
						class="btn preset-filled-success-100-900 h-full font-bold"
						onclick={handleUploadToDatabase}
					>
						<i class="fa-regular fa-floppy-disk"></i>
						Зберегети ціни
					</button>
					<button
						class="btn preset-filled-error-100-900 h-full font-bold"
						onclick={() => (step = 1)}
					>
						<i class="fa-regular fa-circle-xmark"></i>
						Відмінити
					</button>
					{#if hashCheck.loaded_id}
						<div class="badge preset-filled-warning-100-900 h-full">
							<i class="fas fa-exclamation-triangle"></i>
							Увага! Ціни з таким самим вмістом вже існують у базі даних. Буде надано доступ до вже завантажених
							цін.
						</div>
					{/if}
				</div>
				<div class="mt-4">
					{#if processingMessage && !fileTransformed}
						<div class="w-full">
							<p class="text-sm text-gray-700">{processingMessage}</p>
							<div class="h-2.5 w-full rounded-full bg-gray-200">
								<div
									class="h-2.5 rounded-full bg-blue-600"
									style="width: {processingPercentage}%"
								></div>
							</div>
						</div>
					{/if}
					{#if fileTransformed && !uploadedToDB}
						<div class="card preset-tonal-primary mt-4 w-full p-4 text-center">
							<p class="text-md font-bold">Готово до завантаження</p>
						</div>
					{/if}
					{#if uploadedToDB}
						<div class="card preset-tonal-success mt-4 w-full p-4 text-center">
							<p class="text-md font-bold">
								Прайс-лист успішно збережено. Дані постачальника оновлено.
							</p>
						</div>
					{/if}
					{#if errorMessage}
						<p class="text-error-500 mt-2">{errorMessage}</p>
					{/if}
				</div>
			</section>
			<section class="mt-4">
				<h3 class="h5">
					<i class="fa fa-circle-info"></i>
					Інформація про завантаження
				</h3>
				<div class="flex h-9 gap-4">
					<div class="badge preset-filled-surface-100-900 text-md">
						<i class="fas fa-file"></i> Рядків у файлі: {fullFileData.length}
					</div>
					<div class="badge preset-filled-surface-100-900 text-md">
						<i class="fas fa-list"></i> Всього рядків: {transformedData.length}
					</div>
					<div class="badge preset-filled-surface-100-900 text-md">
						<i class="fas fa-circle-check"></i> Прогружено рядків: {uploadedCount} з {totalCount}
					</div>
				</div>
				{#if uploadingToDB}
					<div class="mt-4">
						<p class="text-sm text-gray-700">{uploadDBMessage}</p>
						<div class="mt-2 h-2.5 w-full rounded-full bg-gray-200">
							<div
								class="h-2.5 rounded-full bg-green-600"
								style="width: {uploadDBPercentage}%"
							></div>
						</div>
					</div>
				{/if}
			</section>
		{/if}
	</section>
</main>
