<script lang="ts">
	import { Combobox } from '@skeletonlabs/skeleton-svelte';

	interface ItemData {
		label: string;
		value: string;
	}

	interface Props {
		items: ItemData[];
		label: string;
		placeholder: string;
		name: string;
		value?: string;
		required?: boolean;
		missing?: boolean;
		intialValue?: string;
	}

	let {
		items,
		label,
		placeholder,
		name,
		value = $bindable(),
		required = false,
		missing = false,
		intialValue
	}: Props = $props();

	let selectedCountry = $state<string[]>([]);
	$inspect(selectedCountry, intialValue);

	$effect(() => {
		value = selectedCountry[0];
	});
</script>

<input type="hidden" {name} value={selectedCountry[0]} />

<Combobox
	data={items}
	value={selectedCountry}
	onValueChange={(e) => (selectedCountry = e.value)}
	labelClasses="*:text-sm *:font-normal"
	inputGroupClasses="shadow-none focus-within:outline-2 focus-within:outline-primary-500 h-12 bg-white placeholder:text-gray-400 *:shadow-none *:border-none {missing &&
	!value
		? 'border border-error-400'
		: ''}"
	{label}
	{placeholder}
	{required}
	defaultValue={intialValue ? [intialValue] : []}
>
	{#snippet item(item)}
		<div class="flex w-full justify-between space-x-2 overflow-clip outline-offset-2">
			<span>{item.label}</span>
		</div>
	{/snippet}
</Combobox>
