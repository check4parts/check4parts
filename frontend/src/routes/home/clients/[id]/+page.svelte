<script lang="ts">
	import { enhance } from '$app/forms';
	import ConfirmDeleteModal from '$lib/components/modals/ConfirmDeleteModal.svelte';
	import EditModal from '$lib/components/modals/PropsModal.svelte';
	import type { Tables } from '$lib/database.types.js';
	import toast, { ToastIcon } from 'svelte-french-toast';
	import CarCard from './(components)/CarCard.svelte';
	import ClientTypeBadge from './(components)/ClientTypeBadge.svelte';

	let { data, form } = $props();
	let {
		client,
		types
	}: { client: Tables<'clients'> & { cars: Tables<'cars'>[] }; types: Tables<'client_types'>[] } =
		$derived(data);

	let editPage = $state(false);
	let deleteModalOpen = $state(false);
	let editNameModalOpen = $state(false);
	let editDetailsModalOpec = $state(false);
	let editCarModalOpen = $state(false);
	let deleteCarModalOpen = $state(false);
	let addCarModalOpen = $state(false);
	let selectedCarId = $state('');
	let selectedCar = $derived<Tables<'cars'> | undefined>(
		client.cars.find((car) => car.id.toString() === selectedCarId)
	);

	let selectedTypeId = $state<string>('');
	$effect(() => {
		if (client) {
			selectedTypeId = client.type_id?.toString() ?? '';
		}
	});

	$effect(() => {
		if (form?.success) {
			editPage = false;
			editNameModalOpen = false;
			editDetailsModalOpec = false;
			editCarModalOpen = false;
			addCarModalOpen = false;
			deleteCarModalOpen = false;
			deleteModalOpen = false;
			toast.success(form.message);
		}
		if (!form?.success && form?.message) {
			toast.error("Ой, щось пішло не так...");
		}
	});
</script>

<ConfirmDeleteModal
	title="Ви впевнені, що хочете видалити клієнта '{client.last_name} {client.first_name} {client.middle_name}'?"
	message="Після видалення клієнта, ви не зможете відновити його."
	action="?/delete"
	itemId={client.id}
	bind:open={deleteModalOpen}
/>

<ConfirmDeleteModal
	title="Ви впевнені, що хочете видалити машину '{selectedCar?.name} ({selectedCar?.license_plate})'?"
	message="Після видалення машини, ви не зможете відновити її."
	action="?/deleteCar"
	itemId={selectedCarId}
	bind:open={deleteCarModalOpen}
/>

<EditModal
	bind:openState={editNameModalOpen}
	data={[
		{
			title: 'Імʼя',
			value: client.first_name ?? '',
			placeholder: 'Імʼя',
			type: 'text',
			name: 'first_name'
		},
		{
			title: 'Прізвище',
			value: client.last_name ?? '',
			placeholder: 'Прізвище',
			type: 'text',
			name: 'last_name'
		},
		{
			title: 'По батькові',
			value: client.middle_name ?? '',
			placeholder: 'По батькові',
			type: 'text',
			name: 'middle_name'
		}
	]}
	id={client.id}
	bind:editPage
/>

<EditModal
	bind:openState={editDetailsModalOpec}
	data={[
		{
			title: 'Телефон',
			value: client.phone_number ?? '',
			placeholder: 'Телефон',
			type: 'text',
			name: 'phone'
		},
		{
			title: 'Адреса',
			value: client.address ?? '',
			placeholder: 'Адреса',
			type: 'text',
			name: 'address'
		},
		{
			title: 'Примітки',
			value: client.note ?? '',
			placeholder: 'Примітки',
			type: 'textarea',
			name: 'note'
		}
	]}
	id={client.id}
	bind:editPage
/>

<EditModal
	bind:openState={editCarModalOpen}
	data={[
		{
			title: 'Назва',
			value: selectedCar?.name ?? '',
			placeholder: 'Назва',
			type: 'text',
			name: 'name'
		},
		{
			title: 'VIN',
			value: selectedCar?.vin_code ?? '',
			placeholder: 'VIN',
			type: 'text',
			name: 'vin'
		},
		{
			title: 'Номерний знак',
			value: selectedCar?.license_plate ?? '',
			placeholder: 'Номерний знак',
			type: 'text',
			name: 'license_plate'
		}
	]}
	id={selectedCarId}
	action="?/editCar"
	bind:editPage
/>

<EditModal
	bind:openState={addCarModalOpen}
	title="Додати автомобіль"
	data={[
		{
			title: 'Назва',
			value: '',
			placeholder: 'Назва',
			type: 'text',
			name: 'name'
		},
		{
			title: 'VIN',
			value: '',
			placeholder: 'VIN',
			type: 'text',
			name: 'vin'
		},
		{
			title: 'Номерний знак',
			value: '',
			placeholder: 'Номерний знак',
			type: 'text',
			name: 'license_plate'
		}
	]}
	id={client.id}
	action="?/addCar"
	bind:editPage
/>

<main class="grid gap-6">
	<header class="mb-4 flex items-center justify-between">
		<h1 class="flex items-center gap-2 text-2xl font-bold">
			{client.last_name}
			{client.first_name}
			{client.middle_name}
			{#if editPage}
				<span class="size-7">
					<button onclick={() => (editNameModalOpen = true)}>
						<img src="/edit-button-icon.svg" alt="edit" width="28" height="28" />
					</button>
				</span>
			{/if}
		</h1>
		<div class="flex items-center justify-end">
			{#if editPage}
				<div class="flex gap-2">
					<button
						class="btn preset-outlined-surface-700-300 w-40"
						onclick={() => {
							editPage = false;
						}}
					>
						Скасувати
					</button>
					<form action="?/edit" method="post" class="contents" use:enhance>
						<button class="btn preset-filled-primary-950-50 w-40" type="submit">Зберегти</button>
						<input type="hidden" name="type_id" value={selectedTypeId} />
					</form>
				</div>
			{:else}
				<div class="flex gap-2">
					<button
						class="btn preset-outlined-surface-700-300 w-40"
						onclick={() => (editPage = true)}
					>
						Редагувати
					</button>
					<button
						class="btn preset-filled-error-950-50 w-40"
						onclick={() => (deleteModalOpen = true)}
					>
						Видалити
					</button>
				</div>
			{/if}
		</div>
	</header>
	<section id="client-type">
		<ClientTypeBadge bind:clientType={selectedTypeId} edit={editPage} {types} />
	</section>
	<section id="details">
		<h2 class="h5 flex items-center gap-2">
			Деталі: {#if editPage}
				<span class="size-7">
					<button onclick={() => (editDetailsModalOpec = true)}>
						<img src="/edit-button-icon.svg" alt="edit" width="28" height="28" />
					</button>
				</span>
			{/if}
		</h2>
		<table class="**:border-none table">
			<tbody class="*:nth-[odd]:bg-surface-100">
				<tr>
					<td class="w-1/3 font-bold">Номер телефону:</td>
					<td>{client.phone_number}</td>
				</tr>
				<tr>
					<td class="w-1/3 font-bold">Адреса доставки:</td>
					<td>{client.address}</td>
				</tr>
				<tr>
					<td class="w-1/3 font-bold">Примітки:</td>
					<td>{client.note}</td>
				</tr>
			</tbody>
		</table>
	</section>
	<section id="cars">
		<h2 class="h5">
			Автомобілі:
			<button onclick={() => (addCarModalOpen = true)} class="text-primary-800 ml-2" aria-label="Додати автомобіль">
				<i class="fa-solid fa-circle-plus"></i>
			</button>
		</h2>
		<div class="flex flex-row flex-wrap gap-5">
			{#each client.cars as car}
				<CarCard
					{car}
					bind:carEditModalOpen={editCarModalOpen}
					bind:deleteCarModalOpen
					bind:selectedCarId
				/>
			{/each}
		</div>
	</section>
</main>
