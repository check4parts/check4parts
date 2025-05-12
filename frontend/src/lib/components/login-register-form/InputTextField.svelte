<script lang="ts">
	interface Props {
		lable: string;
		type?: string;
		name: string;
		placeholder: string;
		required?: boolean;
		value?: string;
		missing?: boolean;
		disabled?: boolean;
		invalid?: boolean;
		hide?: boolean;
	}

	let {
		lable,
		type = 'text',
		name,
		placeholder,
		required = false,
		value = $bindable(),
		missing = false,
		disabled = false,
		invalid = false,
		hide = false
	}: Props = $props();
</script>

<label class="label" class:hidden={hide}>
	<span class="label-text text-lg">{lable}</span>
	<input
		class:border-error-400={(missing && !value) || invalid}
		class:border={(missing && !value) || invalid}
		class="input h-16 border-[1.5px]"
		{name}
		{type}
		{placeholder}
		{required}
		{disabled}
		bind:value
	/>
</label>
