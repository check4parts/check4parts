<script lang="ts">
	import { FileUpload } from '@skeletonlabs/skeleton-svelte';
	import StepsBar from './(components)/StepsBar.svelte';
	import { parseJwt } from '$lib/utils/loader/ParseJWT';
	import { processFile } from '$lib/utils/loader/ProcessFile.js';
	import InputSelect from '$lib/components/inputs/modal/InputSelect.svelte';
	import TemplateModal from './(components)/TemplateModal.svelte';
	import { autoMapHeaders, type Template } from '$lib/utils/loader/AutoMap';
	import { transformPreviewData } from '$lib/utils/loader/TransformFile.svelte';

	let { data } = $props();
	let { providers, warehouses } = $derived(data);

	let company_id = $derived<string>(parseJwt(data.session?.access_token || '')?.company_id || '');

	let selected_provider = $state<string>("");
	$inspect('Selected Provider', selected_provider);
	
	let currentProviderWarehouses = $derived(
		warehouses.filter((warehouse) => warehouse.provider_id === selected_provider)
	);

	let step = $state<number>(1);
	let stepState = $state<'current' | 'error' | 'success'>('current');

	let debug = $state(false);

	let uploadedFiles = $state<File[]>([]);
	let fileLoading = $state(false);

	let uploadingToDB = $state(false);
	let uploadedToDB = $state(false);
	let uploadDBMessage = $state('');
	let uploadDBPercentage = $state(0);

	let previewData: any[] = $state([]);
	let fileHeaders: string[] = $state([]);
	let firstRowHeaders: string[] = $state([]);
	let fullFileData: any[] = $state([]);
	let processingMessage = $state('');
	let processingPercentage = $state(0);
	let errorMessage = $state('');

	let templateModalOpenState = $state(false);
	let template = $state<Template>({ metadata: { firstRowHeaders: true }, template: [] });
	let previewTransformedData = $derived(
		transformPreviewData(previewData, template, selected_provider)
	);

	let templateComleated = $derived(
		template.template.reduce((acc, row) => acc && row.header !== '', true) && selected_provider
	);

	$effect(() => {
		if (previewData.length > 0) {
			template.template = autoMapHeaders(Object.values(previewData[0]), currentProviderWarehouses);
			console.log('Template changed:');
		}
	});

	$effect(() => {
		if (step) {
			stepState = 'current';
		}
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
				console.log('Preview Data:', data);
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
			}
		});
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
		// transformingData = false;
		// fileTransformed = false;
		uploadingToDB = false;
		uploadDBMessage = '';
		uploadDBPercentage = 0;
		uploadedToDB = false; // Скидаємо цей стан також
		// hashCheckPromise = null; // Скидаємо проміс перевірки хешу
		// terminateWorkerUpload();
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
/>

<header>
	<h1 class="h4">Завантаження цін постачальників</h1>
	<div class="mt-10 flex items-center justify-center">
		<StepsBar bind:step {stepState} />
	</div>
</header>

<section class="mt-4 max-h-[68vh] overflow-y-auto">
	{#if step === 1 || debug}
		<h2 class="h5 sticky top-0 flex items-center gap-2 bg-white">
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
					console.log('Selected files:', e);
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
						<button class="btn preset-filled-primary-950-50" type="submit" aria-busy={fileLoading}>
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
	{:else if step === 2 || debug}
		<h2 class="h5 sticky top-0 flex items-center gap-2 bg-white">
			<img src="/step-2.svg" alt="Крок 2" /> Крок 2: Перевірте дані
		</h2>
		<section class="mt-4" id="settings">
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
		{/if}
		<section class="mt-4 flex flex-col items-end">
			{#if errorMessage}
				<p class="text-error-500">{errorMessage}</p>
			{/if}
			{#if templateComleated}
				<button
					class="btn preset-filled-primary-950-50 mt-4"
					onclick={() => {
						if (templateComleated) {
							step = 3;
						}
					}}
					disabled={!templateComleated}
				>
					Далі
				</button>
			{:else}
				<p class="text-error-500">
					Будь ласка, налаштуйте всі колонки перед переходом до наступного кроку.
				</p>
			{/if}	
		</section>
	{:else if step === 3 || debug}
		<header>
			<h2 class="h5 flex items-center gap-2">
				<img src="/step-3.svg" alt="Крок 3" /> Крок 3: Завантажте дані в базу
			</h2>
		</header>
	{/if}
</section>
