<script lang="ts">
	import { Switch } from '@skeletonlabs/skeleton-svelte';
	import { Dialog } from 'bits-ui';
	import type { Template } from '$lib/utils/loader/AutoMap';
	import type { SupabaseClient } from '@supabase/supabase-js';
	import toast from 'svelte-french-toast';

	interface Props {
		openState: boolean;
		modalClose?: () => void;
		data: {
			previewData: any[];
			fileHeaders: string[];
			headersLabels: string[];
		};
		template: Template;
		supabase: SupabaseClient;
	}

	let {
		openState = $bindable(false),
		modalClose = () => (openState = false),
		data,
		template = $bindable<Template>(),
		supabase
	}: Props = $props();

	let loadingSaveTemplate = $state(false);

	function handleTemplateChange(index: number, selectedValue: string) {
		const row = template.template.find((r) => r.value === selectedValue);
		const fileHeader = data.fileHeaders[index];

		if (selectedValue === 'ignore') {
			const current = template.template.find((r) => r.header === fileHeader);
			if (current) current.header = '';
			return;
		}

		if (row) {
			template.template.forEach((r) => {
				if (r.header === fileHeader) r.header = '';
			});

			row.header = fileHeader;
		}
	}

	async function saveTemplate() {
		loadingSaveTemplate = true;
		const { error } = await supabase.from('provider_template').upsert({
			provider_id: template.metadata.providerId,
			template: template.template.map((r) => ({ header: r.header, value: r.value })),
		});
		if (error) {
			console.error('Error saving template:', error);
			toast.error('Помилка при збереженні шаблону. Спробуйте ще раз.');
		} else {
			toast.success('Шаблон успішно збережено!');
		}
		loadingSaveTemplate = false;
	}

	function clearTemplate() {
		template.template.forEach((r) => (r.header = ''));
	}
</script>

<Dialog.Root bind:open={openState}>
	<Dialog.Portal>
		<Dialog.Overlay class="fixed inset-0 z-50 bg-black/80" />
		<Dialog.Content
			class="fixed left-1/2 top-1/2 z-50 w-1/2 -translate-x-1/2 -translate-y-1/2 rounded-xl bg-white p-4"
		>
			<div class="flex justify-end">
				<button type="button" onclick={modalClose}>
					<img src="/close-icon.svg" alt="close" class="size-4" />
				</button>
			</div>

			<Dialog.Title class="text-lg font-semibold">Налаштування колонок</Dialog.Title>

			<Dialog.Description class="p-4">
				<div class="mb-4 flex items-center justify-between">
					<p class="text-lg font-semibold">Перший рядок — заголовки</p>
					<Switch
						name="firstRowHeaders"
						label="Перший рядок заголовків"
						checked={template.metadata.firstRowHeaders}
						onCheckedChange={(e) => (template.metadata.firstRowHeaders = e.checked)}
					/>
				</div>

				<div class="max-h-[60vh] overflow-y-auto">
					<table class="w-full border-collapse border-spacing-y-2">
						<tbody>
							{#each data.headersLabels as label, index}
								{@const fileHeader = data.fileHeaders[index]}
								{@const current = template.template.find((r) => r.header === fileHeader)}

								<tr class="grid grid-cols-[2fr_3fr_1fr] items-center align-baseline">
									<td class="max-w-2/3 w-fit py-2 text-lg font-semibold">{label}:</td>
									<td class="py-2 pr-2">
										<select
											class="w-full rounded border p-1"
											value={current?.value ?? 'ignore'}
											onchange={(e) =>
												handleTemplateChange(index, (e.target as HTMLSelectElement).value)}
										>
											<option value="ignore"> -- Ігнорувати -- </option>
											{#each template.template as row}
												<option
													value={row.value}
													disabled={!!row.header && row.header !== fileHeader}
												>
													{row.name}
												</option>
											{/each}
										</select>
									</td>
									<td class="text-surface-300 truncate py-2 pr-2 text-sm">
										( Приклад: {data.previewData[data.previewData.length - 1][index] || '...'} )
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>

				<div class="mt-4 flex justify-end gap-4">
					<button 
						type="button"
						class="btn preset-filled-primary-50-950 flex items-center justify-center font-bold"
						onclick={clearTemplate}
					>
						 Очистит
					</button>
					<button
						type="button"
						class="btn preset-filled-primary-100-900 flex items-center justify-center font-bold"
						onclick={saveTemplate}
						disabled={loadingSaveTemplate}
					>
						{#if loadingSaveTemplate}
							Збереження...
						{:else}
							Зберегти шаблон
						{/if}
					</button>
					<button
						type="button"
						class="btn preset-filled-primary-950-50 font-bold"
						onclick={modalClose}>Готово</button
					>
				</div>
			</Dialog.Description>
		</Dialog.Content>
	</Dialog.Portal>
</Dialog.Root>
