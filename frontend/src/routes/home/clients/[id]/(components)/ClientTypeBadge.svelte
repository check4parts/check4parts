<script lang="ts">
	import type { Tables } from '$lib/database.types';
	import { Select } from 'bits-ui';

	interface Props {
		edit: boolean;
		clientType: string;
		types: Tables<'client_types'>[];
	}

	let { edit, clientType = $bindable(), types }: Props = $props();

	let customAnchor = $state<HTMLElement>(null!);
    let selectedType = $derived(types.find((type) => type.id.toString() === clientType));
</script>

<Select.Root
	type="single"
	onValueChange={(e) => (clientType = e)}
	items={types.map((type) => ({ label: type.name ?? '', value: type.id.toString() }))}
	value={clientType}
>
	<div bind:this={customAnchor} class="w-fit flex items-center gap-1">
		<p class="badge preset-filled-primary-50-950 h-7 text-sm font-bold">
			{selectedType?.name}
        </p>
		{#if edit}
			<Select.Trigger>
				<div class="badge preset-filled-primary-50-950 size-7 p-0">
					<img src="/state-arrow.svg" alt="arrow" height="16" width="16" />
				</div>
			</Select.Trigger>
		{/if}
	</div>
	<Select.Portal>
		<Select.Content
			{customAnchor}
			class="border-primary-950 divide-primary-950 divide-y-1 border-1 z-50 mt-2 flex w-full flex-col rounded-lg bg-white"
		>
			{#each types as type (type.id)}
				<Select.Item value={type.id.toString()}>
					{#snippet children({ selected })}
						<div class="divide-primary-950 flex items-center gap-2 p-2">
							<p class:font-bold={selected}>
								{type.name}
							</p>
						</div>
					{/snippet}
				</Select.Item>
			{/each}
		</Select.Content>
	</Select.Portal>
</Select.Root>
