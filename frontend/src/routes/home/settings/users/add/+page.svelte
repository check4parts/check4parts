<script lang="ts">
	import { enhance } from '$app/forms';
	import InputPasswordField from '$lib/components/card-form/InputPasswordField.svelte';
	import InputSelect from '$lib/components/card-form/InputSelect.svelte';
	import InputTextField from '$lib/components/card-form/InputTextField.svelte';
	import { redirect } from '@sveltejs/kit';
	import toast from 'svelte-french-toast';

	let { data, form } = $props();
	let { points, roles } = $derived(data);

	let password = $state('');
	let repeat_password = $state('');

	let repeat_password_invalid = $derived<boolean>(password !== repeat_password);

	$inspect(form);

	$effect(() => {
		if (form?.success) {
			location.href = '/home/settings/users?success';
		}
		if (form?.error) {
			if (form.error === 'user_already_exists') {
				toast.error('Користувач з такою поштою вже існує');
			} else if (form.error === 'weak_password') {
				toast.error('Пароль має містити мінімум 6 символів');
			} else {
				toast.error('Помилка при додаванні користувача');
			}
		}
		if (form?.missing) {
			toast.error('Заповніть всі поля');
		}
	});
</script>

<header class="flex items-center justify-between">
	<h2 class="h3">Додавання користувача</h2>
	<button
		type="button"
		class="btn preset-filled-primary-950-50"
		onclick={() => {
			location.href = '/home/settings/users?success';
		}}>Тест</button
	>
</header>

<section class="m-5">
	<form
		action="?/add"
		method="post"
		use:enhance={() => {
			return async ({ update }) => {
				update({ reset: false });
			};
		}}
	>
		<div class="grid grid-cols-2 grid-rows-[1fr_0.5fr] gap-5">
			<div class="card preset-filled-surface-50-950 flex w-full flex-col p-8">
				<h3 class="h6">Персональна інформація</h3>
				<div class="flex flex-col gap-10">
					<InputTextField
						lable="Прізвище"
						type="text"
						name="last_name"
						placeholder="Введіть прізвище"
						missing={form?.missing}
					/>
					<InputTextField
						lable="Ім'я"
						type="text"
						name="first_name"
						placeholder="Введіть ім'я"
						missing={form?.missing}
					/>
					<InputTextField
						lable="По батькові"
						type="text"
						name="middle_name"
						placeholder="Введіть по батькові"
						missing={form?.missing}
					/>
				</div>
			</div>

			<div
				class="card preset-filled-surface-50-950 col-start-1 row-start-2 flex w-full flex-col p-8"
			>
				<h3 class="h6">Контактні дані</h3>
				<div class="flex flex-col gap-10">
					<InputTextField
						lable="Номер телефону"
						type="text"
						name="phone"
						placeholder="Введіть номер телефону"
						missing={form?.missing}
					/>
					<InputSelect
						label="Адреса місця роботи"
						name="trading_point"
						placeholder="Оберіть локацію, де працює користувач"
						items={points.map((point) => ({
							label: `${point.name} (${point.street}, ${point.locality})`,
							value: point.id
						}))}
						missing={form?.missing}
					/>
				</div>
			</div>

			<div
				class="card preset-filled-surface-50-950 col-start-2 row-start-1 flex w-full flex-col p-8"
			>
				<h3 class="h6">Дані для входу</h3>
				<div class="flex flex-col gap-10">
					<InputTextField
						lable="Електронна пошта"
						type="email"
						name="email"
						placeholder="Введіть адресу  електронної пошти"
						missing={form?.missing}
					/>
					<InputPasswordField
						lable="Пароль"
						name="password"
						placeholder="Введіть пароль"
						bind:value={password}
						missing={form?.missing}
					/>
					<InputPasswordField
						lable="Повторіть пароль"
						name="repeat_password"
						placeholder="Повторіть пароль"
						bind:value={repeat_password}
						{repeat_password_invalid}
						missing={form?.missing}
					/>
				</div>
			</div>

			<div class="row-start-2 flex h-full flex-col justify-between">
				<div class="card preset-filled-surface-50-950 flex w-full flex-col p-8">
					<h3 class="h6">Роль у системі</h3>
					<div class="flex flex-col gap-10">
						<InputSelect
							label="Посада"
							name="role"
							placeholder="Оберіть посаду користувача"
							items={roles.map((role) => ({ label: role.name, value: role.id }))}
							missing={form?.missing}
						/>
					</div>
				</div>
				<div class="flex justify-end gap-5">
					<a class="btn preset-outlined-primary-950-50 mt-5 w-[10rem]" href="/home/settings/users"
						>Скасувати</a
					>
					<button
						class="btn preset-filled-primary-950-50 mt-5 w-[10rem]"
						type="submit"
						disabled={repeat_password_invalid}
					>
						Додати
					</button>
				</div>
			</div>
		</div>
	</form>
</section>
