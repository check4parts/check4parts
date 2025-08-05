<script lang="ts">
	let {
		lable,
		name,
		placeholder,
		required = false,
		value = $bindable(),
		repeat_password_invalid = $bindable(),
		missing = false,
		disabled = false
	}: {
		lable: string;
		name: string;
		placeholder: string;
		required?: boolean;
		value?: string;
		showPassword?: boolean;
		repeat_password_invalid?: boolean;
		missing?: boolean;
		disabled?: boolean;
	} = $props();

	let showPassword = $state(false);
	let password_valid = $state(false);

	let invalid = $state(false);

	$effect(() => {
		invalid = (!value && missing) || repeat_password_invalid!;
	});
</script>

<label class="label relative block w-full">
	<h6 class="h6">{lable}
		{#if required}
			<span>*</span>
		{/if}
	</h6>
	<input
		class:border-error-400={invalid}
		class:border={invalid}
		class="input focus:outline-primary-500 outline-surface-200 h-12 bg-white px-4 pr-14 shadow-none outline-2 placeholder:text-gray-400"
		{name}
		type={showPassword ? 'text' : 'password'}
		{placeholder}
		{required}
		{disabled}
		bind:value
		oninput={(e: Event) => {
			const target = e.target as HTMLInputElement;
			password_valid = target?.validity?.valid || false;
		}}
	/>
	<button
		type="button"
		class="absolute top-[47%] right-4"
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
