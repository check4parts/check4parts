<script lang="ts">
	import { enhance } from '$app/forms';
	import InputTextField from '$lib/components/login-register-form/InputTextField.svelte';
	import toast from 'svelte-french-toast';
	import ConfrimModal from './(modal)/ConfrimModal.svelte';

	let { form } = $props();

	let current_step = $state<'name' | 'location' | 'contacts'>('name');
	let openModal = $state(false);

	$effect(() => {
		if (form?.success) {
			openModal = true;
		}
		if (form?.missing) {
			toast.error('Заповніть всі поля');
			current_step = 'name';
		}
	})
</script>

<ConfrimModal bind:open={openModal} />

<div class="mx-auto flex h-10/12 w-1/2 flex-col justify-center align-middle">
	<div>
		<h1 class="h1">Реєстрація</h1>
	</div>
	<form method="POST" action="?/register" use:enhance>
		<div class="my-10 flex flex-col gap-10">
			<!-- name -->
			<InputTextField
				lable="Прізвище"
				placeholder="Введіть прізвище"
				name="last_name"
				type="text"
				hide={current_step !== 'name'}
				missing={form?.missing}
			/>
			<InputTextField
				lable="Ім'я"
				placeholder="Введіть ім'я"
				name="first_name"
				type="text"
				hide={current_step !== 'name'}
				missing={form?.missing}
			/>
			<InputTextField
				lable="По батькові"
				placeholder="Введіть по батькові"
				name="middle_name"
				type="text"
				hide={current_step !== 'name'}
				missing={form?.missing}
			/>
			<!-- location -->
			<InputTextField
				lable="Область"
				placeholder="Веддіть область"
				name="region"
				type="text"
				hide={current_step !== 'location'}
				missing={form?.missing}
			/>
			<InputTextField
				lable="Місто"
				placeholder="Введіть місто"
				name="city"
				type="text"
				hide={current_step !== 'location'}
				missing={form?.missing}
			/>
			<InputTextField
				lable="Вулиця"
				placeholder="Введіть вулицю"
				name="street"
				type="text"
				hide={current_step !== 'location'}
				missing={form?.missing}
			/>
			<!-- contacts -->
			<InputTextField
			lable="Назва компанія"
			placeholder="Введіть назву компанії"
			name="company_name"
			type="text"
			hide={current_step !== 'contacts'}
			missing={form?.missing}
		/>
			<InputTextField
				lable="Номер телефону"
				placeholder="Введіть номер телефону"
				name="phone"
				type="text"
				hide={current_step !== 'contacts'}
				missing={form?.missing}
			/>
			<InputTextField
				lable="Електронна пошта"
				placeholder="Введіть  електронну пошту"
				name="email"
				type="email"
				hide={current_step !== 'contacts'}
				missing={form?.missing}
			/>
		</div>
		<div class="grid grid-cols-2 gap-2">
			{#if current_step === 'name'}
				<button
					type="button"
					class="btn preset-filled bg-primary-950 col-start-2 h-12"
					onclick={() => (current_step = 'location')}>Далі</button
				>
			{:else if current_step === 'location'}
				<button
					type="button"
					class="btn preset-outlined h-12"
					onclick={() => (current_step = 'name')}>Назад</button
				>
				<button
					type="button"
					class="btn preset-filled bg-primary-950 h-12"
					onclick={() => (current_step = 'contacts')}>Далі</button
				>
			{:else if current_step === 'contacts'}
				<button
					type="button"
					class="btn preset-outlined h-12"
					onclick={() => (current_step = 'location')}>Назад</button
				>
				<button type="submit" class="btn preset-filled bg-primary-950 h-12">Зареєструватися</button>
			{/if}
		</div>
	</form>
</div>
{#if current_step === 'name'}
	<div class="flex w-full justify-center gap-2">
		<p class="opacity-50">Вже зареєстровані?</p>
		<a href="/auth/login" class="anchor opacity-100">Увіти</a>
	</div>
{/if}
