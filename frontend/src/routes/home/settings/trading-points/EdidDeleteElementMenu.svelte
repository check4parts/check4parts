<script lang="ts">
	import { Tooltip } from 'bits-ui';
	import AddEditPointModal from './AddEditPointModal.svelte';
	import type { ActionData } from './$types';
	import DeleteModalConfirmation from './DeleteModalConfirmation.svelte';

	interface Props {
		point?: {
			id: number;
			name: string;
			region: string;
			locality: string;
			street: string;
		};
		form?: ActionData;
	}

	let { point = $bindable(), form = $bindable() }: Props = $props();

	let editModalOpenState = $state(false);
	let deleteModalOpenState = $state(false);
</script>

{#if editModalOpenState}
	<AddEditPointModal bind:openState={editModalOpenState} type="edit" {point} {form} />
{/if}

{#if deleteModalOpenState}
	<DeleteModalConfirmation bind:open={deleteModalOpenState} {point} />
{/if}

<Tooltip.Provider>
	<Tooltip.Root delayDuration={200}>
		<Tooltip.Trigger class="hidden group-hover:block">
			<img src="/small-menu-icon.svg" alt="edit" class="size-4" />
		</Tooltip.Trigger>
		<Tooltip.Content side="left" class="z-50">
			<div class="card flex flex-col items-start border border-gray-300 bg-white text-xl">
				<button class="px-2" onclick={() => (editModalOpenState = true)}>Редагувати</button>
				<button
					class="w-full border-t border-gray-300 px-2"
					onclick={() => (deleteModalOpenState = true)}>Видалити</button
				>
			</div>
		</Tooltip.Content>
	</Tooltip.Root>
</Tooltip.Provider>
