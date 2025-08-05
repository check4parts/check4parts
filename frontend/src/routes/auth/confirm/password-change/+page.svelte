<script lang="ts">
	import { enhance } from '$app/forms';
	import { goto } from '$app/navigation';
	import InputPasswordField from '$lib/components/inputs/modal/InputPasswordField.svelte';
	import toast from 'svelte-french-toast';

	let { form } = $props();

	let loading = $state(false);
	let password = $state('');
	let repeat_password = $state('');

	let repeatPasswordInvalid = $derived<boolean>(password !== repeat_password);

	$effect(() => {
		if (form) {
			loading = false;
			if (!form.success) {
				toast.error('Щось пішло не так');
				if (form.code == 'same_password') {
					toast.error('Тю, пароль той самий. А треба новий.');
				}
				if (form.code == 'weak_password') {
					toast.error('Пароль має містити мінімум 6 символів');
				}
			}
			if (form.success) {
				toast.success('Пароль успішно змінено');
				goto('/home');
			}
		}
	});
</script>

<section class="m-auto flex w-3/4 flex-col gap-5">
	<form
		class="flex flex-col gap-5"
		method="POST"
		use:enhance={() => {
			return async ({ update }) => {
				update({ reset: false });
			};
		}}
		action="?/changePassword"
		onsubmit={() => (loading = true)}
	>
		<InputPasswordField
			lable="Пароль"
			name="password"
			placeholder="Введіть пароль"
			bind:value={password}
		/>
		<InputPasswordField
			lable="Повторіть пароль"
			name="repeat_password"
			placeholder="Повторіть пароль"
			bind:value={repeat_password}
			repeat_password_invalid={repeatPasswordInvalid}
		/>
		<div class="flex justify-end gap-4">
			<button
				type="submit"
				class="btn preset-filled-primary-950-50 text-xl"
				disabled={repeatPasswordInvalid}
				>{#if loading}
					Завантаження...
				{:else}
					Замінити
				{/if}</button
			>
		</div>
	</form>
</section>
