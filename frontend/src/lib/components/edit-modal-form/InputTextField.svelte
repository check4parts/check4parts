<script lang="ts">
	let {
		lable,
		type = 'text',
		name,
		placeholder,
		required = false,
		value = $bindable(),
		missing = false,
		disabled = false,
		defaultValue
	}: {
		lable: string;
		type?: string;
		name: string;
		placeholder: string;
		required?: boolean;
		value?: string;
		missing?: boolean;
		disabled?: boolean;
		defaultValue?: string;
	} = $props();
</script>

<label class="flex w-full flex-row justify-between">
	<span class="inline-block w-1/2 content-center text-lg font-bold">{lable}</span>
	<input
		class:border-error-400={missing && !value}
		class:border={missing && !value}
		class="input focus:outline-primary-500 outline-surface-200 h-12 w-1/2 bg-white outline-2 placeholder:text-gray-400"
		style="box-shadow: none;"
		{name}
		{type}
		{placeholder}
		{required}
		{disabled}
		bind:value
		{defaultValue}
	/>
</label>
