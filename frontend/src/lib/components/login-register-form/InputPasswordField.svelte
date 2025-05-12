<script lang="ts">
	interface Props {
		lable: string;
		name: string;
		placeholder: string;
		required?: boolean;
		value?: string;
		showPassword?: boolean;
		repeat_password_invalid?: boolean;
		missing?: boolean;
		disabled?: boolean;
		invalid?: boolean;
		valid?: boolean;
	}

	let {
		lable,
		name,
		placeholder,
		required = false,
		value = $bindable(),
		repeat_password_invalid = $bindable(),
		missing = false,
		disabled = false,
		invalid = false,
		valid = $bindable()
	}: Props = $props();

	let showPassword = $state(false);
</script>

<label class="label relative block w-full">
	<span class="label-text text-lg">{lable}</span>
	<input
		class:border-error-400={(!value && missing) || repeat_password_invalid! || invalid}
		class:border={(!value && missing) || repeat_password_invalid! || invalid}
		class="input h-16 border-[1.5px]"
		{name}
		type={showPassword ? 'text' : 'password'}
		{placeholder}
		{required}
		{disabled}
		bind:value
		oninput={(e: Event) => {
			const target = e.target as HTMLInputElement;
			valid = target?.validity?.valid || false;
		}}
	/>
	<button
		type="button"
		class="absolute top-[50%] right-4"
		onmousedown={() => (showPassword = !showPassword)}
		{disabled}
	>
		{#if showPassword}
			<img src="/show-pass.svg" alt="search" class="size-8" />
		{:else}
			<img src="/hide-pass.svg" alt="search" class="size-8" />
		{/if}
	</button>
	{#if repeat_password_invalid}
		<span class="text-error-400 absolute text-sm">Паролі не співпадають</span>
	{/if}
</label>
