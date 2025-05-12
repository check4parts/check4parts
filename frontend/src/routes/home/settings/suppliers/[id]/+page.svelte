<script lang="ts">
	import ConfirmDeleteModal from '$lib/components/modals/ConfirmDeleteModal.svelte';
	import toast from 'svelte-french-toast';
	import ActiveStatteBadge from './(components)/ActiveStatteBadge.svelte';
	import EditModal from './(components)/EditModal.svelte';

	let { data, form } = $props();
	let { supplier } = $derived(data);

	let deleteModalOpen = $state(false);
	let editPage = $state(false);
	let editModalOpen = $state(false);
	let selectedState = $state(supplier.state);

	$effect(() => {
		if (form) {
			if (form?.success) {
				editModalOpen = false;
				toast.success('Дані успішно оновлені', {
					duration: 2000
				});
				editPage = false;
			} else {
				toast.error('Помилка при оновленні даних', {
					duration: 2000
				});
			}
		}
	});
</script>

<ConfirmDeleteModal
	title="Ви впевнені, що хочете видалити постачальника '{supplier.providers.name}'?"
	message="Після видалення постачальника, ви не зможете відновити його."
	action="?/delete"
	itemId={supplier.id}
	bind:open={deleteModalOpen}
/>

<EditModal
	bind:openState={editModalOpen}
	data={supplier.data}
	id={supplier.id}
	{form}
	bind:editPage
/>

<header class="flex items-center justify-end">
	{#if editPage}
		<form action="?/editState" method="post">
			<button
				class="btn preset-outlined-surface-700-300 w-40"
				onclick={() => ((selectedState = supplier.state), (editPage = false))}>Скасувати</button
			>
			<button class="btn preset-filled-primary-950-50 w-40" type="submit">Зберегти</button>
			<input type="hidden" name="id" value={supplier.id} />
			<input type="hidden" name="state" value={selectedState} />
		</form>
	{:else}
		<div>
			<button class="btn preset-outlined-surface-700-300 w-40" onclick={() => (editPage = true)}
				>Редагувати</button
			>
			<button class="btn preset-filled-error-950-50 w-40" onclick={() => (deleteModalOpen = true)}
				>Видалити</button
			>
		</div>
	{/if}
</header>

<section class="m-5 grid grid-cols-[auto_1fr] gap-20">
	<div>
		<img src={supplier.providers.logo_url} alt={supplier.providers.name} class="w-70" />
	</div>
	<div class="flex flex-col gap-5">
		<h3 class="h3">{supplier.providers.name}</h3>
		<ActiveStatteBadge bind:providerState={selectedState} edit={editPage} />
		<div class="mt-5">
			<div class="flex items-center">
				<h4 class="h4">Деталі:</h4>
				{#if editPage}
					<span>
						<button onclick={() => (editModalOpen = true)}>
							<img class="size-7" src="/edit-button-icon.svg" alt="edit" />
						</button>
					</span>
				{/if}
			</div>
			<table class="table **:border-none">
				<tbody class="*:nth-[even]:bg-surface-100">
					{#each supplier.data as data}
						<tr>
							<td class="w-1/3 font-bold">{data.title}</td>
							<td>{data.value}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
</section>
