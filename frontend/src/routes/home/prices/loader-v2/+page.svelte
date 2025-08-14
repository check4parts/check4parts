<script lang="ts">
	import { FileUpload } from '@skeletonlabs/skeleton-svelte';
	import StepsBar from './(components)/StepsBar.svelte';
	import { parseJwt } from '$lib/utils/loader/ParseJWT';
	import { processFile } from '$lib/utils/loader/ProcessFile.js';
	import InputSelect from '$lib/components/inputs/modal/InputSelect.svelte';

	let { data } = $props();
	let { providers } = $derived(data);

	let company_id = $derived<string>(parseJwt(data.session?.access_token || '')?.company_id || '');

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

	let selected_provider = $state<string>('');
	$inspect(selected_provider);

	$effect(() => {
		if (step) {
			stepState = 'current';
		}
	});

	async function handleFileUpload() {
		uploadedToDB = false;

		await processFile(uploadedFiles, 1, 5, 0, {
			onPreview: ({ previewData: data, metadata }) => {
				console.log('Preview Data:', data);
				previewData = data;
				fileHeaders = metadata.headers;
				firstRowHeaders = Object.values(data[0]);
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
		console.log('Full file data:', fullFileData.length);
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

<header>
	<h1 class="h4">Завантаження цін постачальників</h1>
	<div class="mt-10 flex items-center justify-center">
		<StepsBar bind:step {stepState} />
	</div>
</header>

<section>
	{#if step === 1 || debug}
		<h2 class="h5 flex items-center gap-2">
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
	{/if}
	{#if step === 2 || debug}
		<h2 class="h5 flex items-center gap-2">
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
					/>
				</div>
			</div>
		</section>
		<section class="mt-4" id="basic-info">
			<div class="flex h-9 gap-4">
				<div class="badge preset-filled-primary-50-950 text-md">
					<i class="fas fa-file"></i>
					Розмір: {uploadedFiles.length > 0 ? formatFileSize(uploadedFiles[0].size) : '0 B'}
				</div>
				<div class="badge preset-filled-primary-50-950 text-md">
					<i class="fas fa-list"></i> Рядків: {fullFileData.length}
				</div>
				<div class="badge preset-filled-primary-50-950 text-md">
					<i class="fas fa-calendar"></i> Дата: {uploadedFiles
						? new Date(uploadedFiles[0].lastModified).toLocaleDateString('uk')
						: 'N/A'}
				</div>
			</div>
		</section>
		<section class="mt-4" id="dataPreview">
			{#if previewData.length > 0}
					<div class="border-primary-950 overflow-hidden rounded-xl border-2">
						<div class="max-h-[70vh] overflow-y-auto">
							<table class="table min-w-full border-collapse table-auto">
								<thead class="bg-primary-950 sticky top-0 z-10">
									<tr class="text-primary-50">
										{#each fileHeaders as header}
                      <th class="px-4 py-2 text-left">{header}</th>
                    {/each}
									</tr>
								</thead>
								<tbody class="!divide-primary-950 !divide-y-2">
									{#each previewData as row}
										<tr class="hover:bg-primary-50 group w-full divide-x-2">
                      {#each Object.values(row) as cell}
                        <td class="px-4 py-2 whitespace-nowrap">{cell}</td>
                      {/each}
                    </tr>
									{/each}
								</tbody>
							</table>
						</div>
					</div>
			{/if}
		</section>
	{/if}
</section>
