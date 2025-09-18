<script lang="ts">
	import Menu from './(components)/Menu.svelte';
	import { page } from '$app/state';
	import SearchInput from '$lib/components/inputs/search-bar/SearchInput.svelte';
	import { goto } from '$app/navigation';

	let { data, children } = $props();
	let { supabase } = $derived(data);

	let currentPage = $derived(page.route.id?.split('/')[2]!);

	const logout = async () => {
		const { error } = await supabase.auth.signOut();
		if (error) {
			console.error(error);
		}
		window.location.href = '/auth';
	};
</script>

<main class="grid h-screen w-screen grid-cols-[auto_1fr] grid-rows-[auto_1fr] gap-5 px-3 py-5">
	<h1 class="h5 flex h-full items-center uppercase">check4parts</h1>
	<section class="min-w-2xs">
		<div class="flex h-full w-full items-center justify-start gap-2">
			<div class="w-2/6 min-w-[220px]">
				<SearchInput
					name="search"
					placeholder="Пошук запчастини"
					gotoOnSearch={(value) => {
						goto(`/home/search?q=${value}`);
					}}
				/>
			</div>
			<div class="w-1/6 min-w-[220px]">
				<SearchInput
					name="search"
					placeholder="Пошук по VIN коду"
					gotoOnSearch={(value) => {
						goto(`/home/search-vin?q=${value}`);
					}}
				/>
			</div>
		</div>
	</section>

	<menu class="flex h-full flex-col gap-2 transition-all">
		<div class="h-full min-w-3xs overflow-auto">
			<Menu page={currentPage} />
		</div>
		<div>
			<a
				class="flex items-center gap-2 text-xl"
				href="/home/profile"
				class:font-bold={currentPage === 'profile'}
			>
				<img
					src={currentPage === 'profile' ? '/cubes-icon-selected.svg' : '/cubes-icon.svg'}
					alt="Профіль користувача"
					class=" size-6"
				/>
				Профіль користувача
			</a>
			<button class="flex items-center gap-2 text-xl" onclick={logout}>
				<img src="/settings-icon.svg" alt="Вийти" class=" size-6" />
				Вийти
			</button>
		</div>
	</menu>
	<section class="overflow-y-auto rounded-3xl border-[1.5rem] border-white bg-white h-full">
		{@render children()}
	</section>
</main>
