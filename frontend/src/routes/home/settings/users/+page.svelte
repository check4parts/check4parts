<script lang="ts">
	let { data } = $props();
	let { staff } = $derived(data);

	let modalOpenState = $state(false);

	let search = $state<string>('');
	let searchQuery = $derived(search.toLocaleLowerCase());
	let filteredStaff = $derived(
		staff.filter((person) =>
			[
				person.name,
				person.roles.name,
				person.trading_points?.name,
				person.trading_points?.street,
				person.trading_points?.locality
			].some((field) => field?.toLowerCase().includes(searchQuery))
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
	<label class="relative block w-full focus-within:text-gray-500">
		<img src="/search-icon.svg" alt="search" class="absolute top-1/5 left-4 size-6" />
		<input
			type="search"
			name="search"
			id="search"
			bind:value={search}
			placeholder="Пошук за ПІБ, посадою, адрессою"
			class="input h-10 w-1/3 appearance-none rounded-3xl px-4 py-3 pl-14 placeholder:text-sm focus:outline-none"
		/>
	</label>
</section>

{#if staff.length > 0}
	<section class="flex flex-col gap-4">
		<div class="border-primary-950 overflow-hidden rounded-xl border-2">
			<div class="max-h-[75vh] overflow-y-auto">
				<table class="table min-w-full border-collapse">
					<thead class="bg-primary-950 sticky top-0 z-10">
						<tr class="text-primary-50">
							<th class="w-1/3">ПІБ</th>
							<th class="w-1/3">Посда</th>
							<th class="w-1/3">Адреса</th>
						</tr>
					</thead>
					<tbody class="!divide-primary-950 !divide-y-2">
						{#each filteredStaff as person (person.id)}
							<tr class="divide-primary-950 group hover:bg-primary-50 w-full divide-x-2">
								<td class="w-1/3">
								<a href="/home/settings/users/{person.id}">
									{person.name}
								</a>
								</td>
								<td class="w-1/3">{person.roles.name}</td>
								<td class="w-1/3"
									>{person.trading_points
										? `${person.trading_points.name} (${person.trading_points.street}, ${person.trading_points.locality})`
										: '(не додано)'}</td
								>
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
