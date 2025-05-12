<script lang="ts">
	import InputPasswordField from '$lib/components/login-register-form/InputPasswordField.svelte';
	import InputTextField from '$lib/components/login-register-form/InputTextField.svelte';
	import { isValidEmail } from '$lib/validation/email.js';

	let { form } = $props();

	let invalidCredentials = $derived(form?.code == 'invalid_credentials');

	let email = $state(form?.form.email);
	let email_valid = $derived(isValidEmail(email));
	let password_valid = $state(false);
	let disabled = $derived(!(password_valid && email_valid));
</script>

<div class="mx-auto flex h-10/12 w-1/2 flex-col justify-center align-middle">
	<div>
		<h1 class="h1">Вхід у систему</h1>
		<p>Порівнюйте ціни, керуйте складськими запасами та замовленнями — все в одному місці.</p>
	</div>
	<form method="POST" action="?/login">
		<div class="my-10 flex flex-col gap-10">
			<InputTextField
				lable="Електронна пошта"
				type="email"
				name="email"
				placeholder="Введіть адресу  електронної пошти"
				required
				bind:value={email}
				invalid={invalidCredentials || !!(!email_valid && email)}
			/>
			<InputPasswordField
				lable="Пароль"
				name="password"
				placeholder="Введіть пароль"
				invalid={invalidCredentials}
				bind:valid={password_valid}
				required
			/>
		</div>

		<div class="grid grid-cols-2">
			<div>
				{#if invalidCredentials}
					<p class="h-12 align-middle text-red-500">Невірний логін або пароль!</p>
				{/if}
			</div>
			<button type="submit" class="btn preset-filled bg-primary-950 h-12" {disabled}>Увійти</button>
		</div>
	</form>
</div>
<div class="flex w-full justify-center gap-2">
	<p class="opacity-50">Ще не зареєстровані?</p>
	<a href="/auth/registration" class="anchor opacity-100">Створити обліковий запис</a>
</div>
