<script lang="ts">
	import { Tooltip } from 'bits-ui';
	import type { Snippet } from 'svelte';
	import ConfirmDeleteModal from '../modals/ConfirmDeleteModal.svelte';

	interface Props {
		editModalOpenState?: boolean;
		deleteModalOpenState?: boolean;
		editOnClick?: () => void;
		deleteOnClick?: () => void;
		editLink?: string;
		deleteLink?: string;
		editModal?: Snippet;
		deleteModal?: Snippet;
		deleteModalConfigs?: {
			title: string;
			message: string;
			action: string;
			itemId: string;
		};
	}

	let {
		editModalOpenState = $bindable(false),
		deleteModalOpenState = $bindable(false),
		editOnClick,
		deleteOnClick,
		editLink,
		deleteLink,
		deleteModalConfigs
	}: Props = $props();
</script>

<!-- {#if deleteModalOpenState} -->
<!-- {/if} -->


<ConfirmDeleteModal {...deleteModalConfigs!} bind:open={deleteModalOpenState} />

	<Tooltip.Provider>
	<Tooltip.Root delayDuration={200}>
		<Tooltip.Trigger class="hidden group-hover:block">
			<img src="/small-menu-icon.svg" alt="edit" class="size-4" />
		</Tooltip.Trigger>
		<Tooltip.Content side="left" class="z-50">
			<div class="card flex flex-col items-start border border-gray-300 bg-white text-xl">
				{#if editLink}
					<a href={editLink} class="px-2">Редагувати</a>
				{:else}
					<button class="px-2" onclick={() => editOnClick?.() || (editModalOpenState = true)}
						>Редагувати</button
					>
				{/if}
				{#if deleteLink}
					<a href={deleteLink} class="w-full border-t border-gray-300 px-2">Видалити</a>
				{:else}
					<button
						class="w-full border-t border-gray-300 px-2"
						onclick={() => deleteOnClick?.() || (deleteModalOpenState = true)}>Видалити</button
					>
				{/if}
			</div>
		</Tooltip.Content>
	</Tooltip.Root>
</Tooltip.Provider>
