<script lang="ts">
	import { Select } from 'bits-ui';

	interface Props {
		edit: boolean;
		providerState: string;
	}

	interface StateData {
		label: string;
		value: string;
		icon: string;
	}

	const statesData: StateData[] = [
		{ label: 'Активний', value: 'active', icon: '/active-icon.svg' },
		{ label: 'Призупинено', value: 'paused', icon: '/paused-icon.svg' }
	];

	let { edit, providerState = $bindable() }: Props = $props();

	let selectedState = $derived(statesData.find((state) => state.value === providerState));
	let customAnchor = $state<HTMLElement>(null!);
</script>

<Select.Root
	type="single"
	onValueChange={(e) => (providerState = e)}
	items={statesData}
	value={providerState}
>
	<div bind:this={customAnchor} class="w-fit">
		<div class="badge preset-filled-primary-50-950 h-7 text-sm font-bold">
			<img src={selectedState?.icon} alt={selectedState?.label} class="size-4" />
			{selectedState?.label}
		</div>
		{#if edit}
			<Select.Trigger>
				<div class="badge preset-filled-primary-50-950 size-7 p-0">
					<img src="/state-arrow.svg" alt="arrow" />
				</div>
			</Select.Trigger>
		{/if}
	</div>
	<Select.Portal>
		<Select.Content
			{customAnchor}
			class="border-primary-950 divide-primary-950 z-50 mt-2 flex w-full flex-col divide-y-1 rounded-lg border-1 bg-white"
		>
			{#each statesData as state, i (i + state.value)}
				<Select.Item value={state.value}>
					{#snippet children({ selected })}
						<div class="divide-primary-950 flex items-center gap-2 p-2">
							<img src={state?.icon} alt={state?.label} class="size-4" />
							<p class:font-bold={selected}>
								{state.label}
							</p>
						</div>
					{/snippet}
				</Select.Item>
			{/each}
		</Select.Content>
	</Select.Portal>
</Select.Root>
