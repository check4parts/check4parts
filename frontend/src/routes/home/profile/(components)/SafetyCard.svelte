<script lang="ts">
	import EditPassword from './EditPassword.svelte';

	interface Props {
		last_login?: string;
		form: any;
	}

	let { last_login, form = $bindable() }: Props = $props();

	let editPasswordModalOpenState = $state(false);

	$effect(() => {
		if (form) {
			if (form?.success) {
				editPasswordModalOpenState = false;
			}
		}
	});
</script>

<EditPassword
	bind:openState={editPasswordModalOpenState}
	modalClose={() => {
		editPasswordModalOpenState = false;
	}}
/>

<section
	class="mt-15 shadow-surface-50 mx-auto rounded-xl p-8 shadow-[0px_0px_9px_17px_rgba(0,_0,_0,_0.1)]"
>
	<header class="mb-4 flex items-center justify-between rounded-xl">
		<h3 class="h5">Безпека</h3>
	</header>
	<div class="flex flex-col gap-4">
		{#if last_login}
			<div class="flex h-6 w-full items-center gap-4">
				<h4 class="text-surface-200 w-40 font-bold">Останій вхід</h4>
				<p class="text-primary-950-50">{new Date(last_login).toLocaleString('uk-UA')}</p>
			</div>
		{/if}
		<div class="flex items-center gap-4">
			<h4 class="text-surface-200 w-40 font-bold">Пароль</h4>
			<button
				type="button"
				class="btn-sm preset-outlined-primary-950-50 rounded-md !border-2 font-bold"
				onclick={() => (editPasswordModalOpenState = true)}>Змінити</button
			>
		</div>
	</div>
</section>
