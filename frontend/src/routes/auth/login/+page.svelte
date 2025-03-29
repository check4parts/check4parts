<script lang="ts">
	import { isValidEmail } from '$lib/validation/email.js';

	let { form } = $props();

	let invalidCredentials = $derived(form?.code == 'invalid_credentials');

	let email = $state(form?.form.email);
	let email_valid = $derived(isValidEmail(email));
	let password_valid = $state(false);
	let disabled = $derived(!(password_valid && email_valid));

	$inspect(disabled, email, email_valid, password_valid);
</script>

<div class="m-auto flex h-10/12 w-1/2 flex-col justify-around align-middle">
	<div>
		<h1 class="h1">Вхід у систему</h1>
		<p>Порівнюйте ціни, керуйте складськими запасами та замовленнями — все в одному місці.</p>
	</div>
	<form method="POST" action="?/login" class="flex flex-col gap-10">
		<label class="label">
			<span class="label-text text-lg">Електронна пошта</span>
			<input
				class:border-error-400={invalidCredentials}
				class:border-error-500={!email_valid && email}
				class:border-primary-400={email_valid}
				class="input h-16 border"
				name="email"
				type="email"
				placeholder="Введіть адресу  електронної пошти"
				required
				bind:value={email}
			/>
		</label>
		<label class="label">
			<span class="label-text text-lg">Пароль</span>
			<input
				class:border-error-400={invalidCredentials}
				class="input h-16 border"
				type="password"
				name="password"
				placeholder="Введіть пароль"
				required
				oninput={(e: Event) => {
					const target = e.target as HTMLInputElement;
					password_valid = target?.validity?.valid || false;
				}}
			/>
		</label>
		<div class="grid grid-cols-2">
			<div>
				{#if invalidCredentials}
					<p class="h-12 align-middle text-red-500">Невірний логін або пароль!</p>
				{/if}
			</div>
			<button type="submit" class="btn preset-filled bg-primary-950 h-12" {disabled}>Увійти</button>
		</div>
	</form>
	<div class="flex w-full justify-center gap-2">
		<p class="opacity-50">Ще не зареєстровані?</p>
		<a href="/auth/registration" class="anchor opacity-100">Створити обліковий запис</a>
	</div>
</div>
