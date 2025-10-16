<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import SmallSearchInput from '$lib/components/inputs/search-bar/SmallSearchInput.svelte';
	import EdidDeleteElementMenu from '$lib/components/modals/EditDeleteModalInTable.svelte';
	import toast from 'svelte-french-toast';

	let { data, form } = $props();
	let { staff } = $derived(data);

	const isSuccess = page.url.searchParams.has('success');
	$effect(() => {
		if (isSuccess) {
			toast.success('Користувача успішно додано', {
				duration: 2000
			});
			goto('/home/settings/users', { replaceState: true, noScroll: true, keepFocus: true });
		}
		if (form) {
			if (form.success) {
				toast.success('Користувача успішно видалено', {
					duration: 2000
				});
			}
			if (!form.success) {
				toast.error('Помилка при видаленні користувача', {
					duration: 2000
				});
			}
		}
	});

	let search = $state<string>('');
	let search_query = $derived(search.toLocaleLowerCase());
	let filtered_staff = $derived(
		staff.filter((person) =>
			[
				person.first_name,
				person.last_name,
				person.middle_name,
				person.roles?.name,
				person.trading_points?.name,
				person.trading_points?.street,
				person.trading_points?.locality
			].some((field) => field?.toLowerCase().includes(search_query))
		)
	);
</script>

{#snippet noStaffMessage()}
	<div class="flex h-full w-full flex-col items-center justify-center">
		<h3 class="h5">Тут поки що порожньо.</h3>
		<p>Додайте першого користувача, щоб розпочати роботу.</p>
	</div>
{/snippet}

<header class="flex items-center justify-between">
	<h2 class="h3">Користувачі</h2>
	<a class="btn preset-filled-primary-950-50" href="/home/settings/users/add">Додати користувача</a>
</header>
<section class="my-5 flex items-center justify-between">
	<!-- <label class="relative block w-full focus-within:text-gray-500">
		<img src="/search-icon.svg" alt="search" class="absolute top-1/5 left-4 size-6" />
		<input
			type="text"
			name="search"
			id="search"
			bind:value={search}
			placeholder="Пошук за ПІБ, посадою, адрессою"
			class="input h-10 w-1/3 appearance-none rounded-3xl px-4 py-3 pl-14 placeholder:text-sm focus:outline-none"
		/>
	</label> -->
	<SmallSearchInput 
		bind:value={search}
		placeholder="Пошук за ПІБ, посадою, адрессою"
		class="w-1/3"
	/>
</section>

{#if staff.length > 0}
	<section class="flex flex-col gap-4">
		<div class="border-primary-950 overflow-hidden rounded-xl border-2">
			<div class="max-h-[70vh] overflow-y-auto">
				<table class="table min-w-full border-collapse">
					<thead class="bg-primary-950 sticky top-0 z-10">
						<tr class="text-primary-50">
							<th class="w-1/3">ПІБ</th>
							<th class="w-1/3">Посда</th>
							<th class="w-1/3">Адреса</th>
						</tr>
					</thead>
					<tbody class="!divide-primary-950 !divide-y-2">
						{#each filtered_staff as person (person.id)}
							<tr class="divide-primary-950 group hover:bg-primary-50 w-full divide-x-2">
								<td class="w-1/3">
									{person.first_name}
									{person.last_name}
								</td>
								<td class="w-1/3">{person.roles.name}</td>
								<td class="flex items-center justify-between">
									<p class="w-6/7">
										{person.trading_points
											? `${person.trading_points.name} (${person.trading_points.street}, ${person.trading_points.locality})`
											: '(не додано)'}
									</p>
									<EdidDeleteElementMenu
										editLink={`/home/settings/users/${person.id}`}
										deleteModalConfigs={{
											title: `Видалення користувача ${person.first_name}`,
											message: 'Ви дійсно хочете видалити користувача?',
											action: '?/delete',
											itemId: person.id
										}}
									/>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	</section>
{:else}
	<section class="h-2/3">
		{@render noStaffMessage()}
	</section>
{/if}
