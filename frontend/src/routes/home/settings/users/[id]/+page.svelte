<script lang="ts">
	import InputPasswordField from '$lib/components/card-form/InputPasswordField.svelte';
	import InputSelect from '$lib/components/card-form/InputSelect.svelte';
	import InputTextField from '$lib/components/card-form/InputTextField.svelte';
	import toast from 'svelte-french-toast';

	let { data, form } = $props();
	let { user, roles, points } = $derived(data);

	let password = $state('');
	let repeat_password = $state('');
	let repeat_password_invalid = $derived<boolean>(password !== repeat_password);

	$effect(() => {
		if (form) {
			if (form.success) {
				toast.success('Користувача успішно змінено');
			} else {
				toast.error('Помилка при редагуванні користувача');
			}
		}
	});
</script>

<header class="flex items-center justify-between">
	<h2 class="h3">Редагування користувача</h2>
</header>

<section class="m-5">
	<form action="?/edit" method="post">
		<input type="hidden" name="id" value={user.id} />
		<div class="grid grid-cols-2 grid-rows-[1fr_0.5fr] gap-5">
			<div class="card preset-filled-surface-50-950 flex w-full flex-col p-8">
				<h3 class="h6">Персональна інформація</h3>
				<div class="flex flex-col gap-10">
					<InputTextField
						lable="Прізвище"
						type="text"
						name="last_name"
						placeholder="Введіть прізвище"
						value={user.last_name}
					/>
					<InputTextField
						lable="Ім'я"
						type="text"
						name="first_name"
						placeholder="Введіть ім'я"
						value={user.first_name}
					/>
					<InputTextField
						lable="По батькові"
						type="text"
						name="middle_name"
						placeholder="Введіть по батькові"
						value={user.middle_name}
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
						value={user.phone_number}
					/>
					<InputSelect
						label="Адреса місця роботи"
						name="trading_point"
						placeholder="Оберіть локацію, де працює користувач"
						items={points.map((point) => ({
							label: `${point.name} (${point.street}, ${point.locality})`,
							value: point.id
						}))}
						intialValue={user.trading_point_id}
					/>
				</div>
			</div>

			<div
				class="card preset-filled-surface-50-950 col-start-2 row-start-1 flex w-full flex-col p-8"
			>
				<h3 class="h6">Дані для входу</h3>
				<div class="flex flex-col gap-10">
					<InputTextField
						lable="Email"
						type="email"
						name="email"
						placeholder="Введіть адресу  електронної пошти"
						value={user.email}
						disabled
					/>
					<InputPasswordField
						lable="Пароль"
						name="password"
						placeholder="Введіть пароль"
						disabled
						bind:value={password}
					/>
					<InputPasswordField
						lable="Повторіть пароль"
						name="repeat_password"
						placeholder="Повторіть пароль"
						disabled
						{repeat_password_invalid}
						bind:value={repeat_password}
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
							items={roles.map((role) => ({
								label: role.name,
								value: role.id
							}))}
							intialValue={user.role_id}
						/>
					</div>
				</div>
				<div class="flex justify-end gap-5">
					<a class="btn preset-outlined-primary-950-50 mt-5 w-[10rem]" href="/home/settings/users"
						>Скасувати</a
					>
					<button
						class="btn preset-filled-primary-950-50 mt-5 flex w-[10rem] items-center justify-center gap-2"
						type="submit"
					>
						Зберегти
					</button>
				</div>
			</div>
		</div>
	</form>
</section>
