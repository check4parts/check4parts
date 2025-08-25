<script lang="ts">
	let {
		lable,
		type = 'text',
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
	<h6 class="h6">
		{lable}
		{#if required}
			<span>*</span>
		{/if}
	</h6>
	<input
		class:border-error-400={missing && !value}
		class:border={missing && !value}
		class="input focus:outline-primary-500 outline-surface-200 h-12 bg-white outline-2 placeholder:text-gray-400"
		style="box-shadow: none;"
		{name}
		{type}
		{placeholder}
		{required}
		{disabled}
		bind:value
	/>
</label>
