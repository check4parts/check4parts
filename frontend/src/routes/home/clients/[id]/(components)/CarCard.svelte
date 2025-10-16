<script lang="ts">
	import EditDeleteModalInTable from '$lib/components/modals/EditDeleteModalInTable.svelte';
	import type { Tables } from '$lib/database.types';
	import { Tooltip } from 'bits-ui';

	interface Props {
		carEditModalOpen: boolean;
		deleteCarModalOpen: boolean;
		selectedCarId: string;
		car: Tables<'cars'>;
	}

	let {
		carEditModalOpen = $bindable(false),
		deleteCarModalOpen = $bindable(false),
		selectedCarId = $bindable(''),
		car
	}: Props = $props();
</script>

{#snippet editDeleteMenu()}
	<Tooltip.Provider>
		<Tooltip.Root delayDuration={200}>
			<Tooltip.Trigger>
				<img src="/small-menu-icon.svg" alt="edit" class="size-4" />
			</Tooltip.Trigger>
			<Tooltip.Content side="left" class="z-50 text-lg">
				<div class="card flex flex-col items-start border border-gray-300 bg-white">
					<button
						class="px-2"
						onclick={() => {
							selectedCarId = car.id.toString();
							carEditModalOpen = true;
						}}
					>
						Редагувати
					</button>
					<button
						class="w-full border-t border-gray-300 px-2"
						onclick={() => {
							selectedCarId = car.id.toString();
							deleteCarModalOpen = true;
						}}
					>
						Видалити
					</button>
				</div>
			</Tooltip.Content>
		</Tooltip.Root>
	</Tooltip.Provider>
{/snippet}

<div class="card bg-primary-50 w-fit p-5">
	<header class="mb-4 flex flex-row items-center justify-between px-2">
		<h4 class="text-md font-semibold">{car.name}</h4>
		{@render editDeleteMenu()}
	</header>
	<table class="**:border-none table">
		<tbody>
			<tr>
				<td class="font-semibold">VIN-код:</td>
				<td>{car.vin_code}</td>
			</tr>
			<tr>
				<td class="font-semibold">Номерний знак:</td>
				<td>{car.license_plate}</td>
			</tr>
		</tbody>
	</table>
</div>
