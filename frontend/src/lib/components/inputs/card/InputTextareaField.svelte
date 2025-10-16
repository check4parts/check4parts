<script lang="ts">
	let {
		lable,
		name,
		placeholder,
		required = false,
		value = $bindable(),
		missing = false,
		disabled = false
	}: {
		lable: string;
		type?: string;
		name: string;
		placeholder: string;
		required?: boolean;
		value?: string;
		missing?: boolean;
		disabled?: boolean;
	} = $props();
</script>

<label class="label">
	<span class="text-sm"
		>{lable}
		{#if required}
			<span>*</span>
		{/if}</span
	>
	<textarea
		class:border-error-400={missing && !value}
		class:border={missing && !value}
		class="textarea focus:outline-primary-500 bg-white placeholder:text-gray-400 focus:outline-2"
		style="box-shadow: none;"
		{name}
		{placeholder}
		{required}
		{disabled}
		bind:value
	></textarea>
</label>
