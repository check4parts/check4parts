<script lang="ts">
	let {
		lable,
		name,
		placeholder,
		value = $bindable(),
		missing = false,
		disabled = false,
		defaultValue
	}: {
		lable: string;
		type?: string;
		name: string;
		placeholder: string;
		value?: string;
		missing?: boolean;
		disabled?: boolean;
		defaultValue?: string;
	} = $props();
</script>

<label class="flex w-full flex-row justify-between">
	<span class="inline-block w-1/2 content-normal text-lg font-bold">{lable}</span>
	<textarea
		class:border-error-400={missing && !value}
		class:border={missing && !value}
		class="textarea focus:outline-primary-500 outline-surface-200 w-1/2 bg-white outline-2 placeholder:text-gray-400"
		style="box-shadow: none;"
		rows="3"
		{name}
		{placeholder}
		{disabled}
		bind:value
		{defaultValue}
	></textarea>
</label>
