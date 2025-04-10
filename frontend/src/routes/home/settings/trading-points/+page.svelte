<script lang="ts">
	import EditDeleteModel from '$lib/components/table/EditDeleteModel.svelte';
	import toast from 'svelte-french-toast';
	import type { PageProps } from './$types';
	import AddEditPointModal from './AddEditPointModal.svelte';

	let { data, form }: PageProps = $props();
	let { points } = $derived(data);

	let modalOpenState = $state(false);
</script>

{#snippet noPointsMessage()}
	<div class="flex h-full w-full flex-col items-center justify-center">
		<h3 class="h5">Тут поки що порожньо.</h3>
		<p>Додайте першу торгову точку, щоб розпочати роботу.</p>
	</div>
{/snippet}

<header class="flex items-center justify-between">
	<h2 class="h3">Торгові точки</h2>

	<button
		type="button"
		class="btn preset-filled-primary-950-50"
		onclick={() => (modalOpenState = true)}>Додати торгову точку</button
	>
	{#if modalOpenState}
		<AddEditPointModal bind:openState={modalOpenState} type="add" {form} />
	{/if}
</header>
<section class="mt-10 flex flex-col gap-4">
	{#if points.length > 0}
		<div class="border-primary-950 overflow-hidden rounded-xl border-2">
			<div class="max-h-[75vh] overflow-y-auto">
				<table class="table min-w-full border-collapse">
					<thead class="bg-primary-950 sticky top-0 z-10">
						<tr class="text-primary-50">
							<th>Назва</th>
							<th>Адреса</th>
						</tr>
					</thead>
					<tbody class="!divide-primary-950 !divide-y-2">
						{#each points as point (point.id)}
							<tr class="divide-primary-950 group hover:bg-primary-50 w-full divide-x-2">
								<td class="w-1/2">{point.name}</td>
								<td class="flex items-center justify-between">
									<p>
										{point.locality}
										{point.street}
									</p>
									<EditDeleteModel
										deleteModalConfigs={{
											title: `Видалення торгової точки ${point.name}`,
											message: 'Ви дійсно хочете видалити торгову точку?',
											action: '?/delete',
											itemId: point.id
										}}
									>
										{#snippet editModal(closeModal)}
											<AddEditPointModal
												openState={true}
												modalClose={closeModal}
												type="edit"
												{point}
												{form}
											/>
										{/snippet}
									</EditDeleteModel>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	{:else}
		{@render noPointsMessage()}
	{/if}
</section>
