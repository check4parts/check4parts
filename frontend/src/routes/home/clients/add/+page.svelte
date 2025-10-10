<script lang="ts">
	import { enhance } from '$app/forms';
	import toast from 'svelte-french-toast';
	import AdditionaInfo from './(cards)/AdditionaInfo.svelte';
	import CarsInfo from './(cards)/CarsInfo.svelte';
	import ClientType from './(cards)/ClientType.svelte';
	import PersonalInfo from './(cards)/PersonalInfo.svelte';

	let { data, form } = $props();
	let { types } = $derived(data);

	$effect(() => {
		if (form?.success) {
			location.href = '/home/clients?success';
		}
		if (form?.error) {
			toast.error('Помилка при додаванні клієнта');
		}
		if (form?.missing) {
			toast.error('Заповніть всі поля');
		}
	});
</script>

<header class="flex items-center justify-between">
	<h2 class="h3">Додавання Клієнта</h2>
</header>

<section class="mt-5">
	<form
		action="?/add"
		method="post"
		use:enhance={() => {
			return async ({ update }) => {
				update({ reset: false });
			};
		}}
	>
		<div class="flex flex-row flex-wrap gap-5 *:w-[49%]">
			<CarsInfo />
			<PersonalInfo missing={form?.missing} />
			<AdditionaInfo missing={form?.missing} />
			<div class="flex-end flex flex-col justify-between">
				<ClientType {types} />
				<div class="flex justify-end gap-5">
					<a class="btn preset-outlined-primary-950-50 mt-5 w-[10rem]" href="/home/clients">
						Скасувати
					</a>
					<button class="btn preset-filled-primary-950-50 mt-5 w-[10rem]" type="submit">
						Додати
					</button>
				</div>
			</div>
		</div>
	</form>
</section>
