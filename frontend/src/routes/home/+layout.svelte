<script lang="ts">
	import Menu from './(components)/Menu.svelte';
	import { page } from '$app/state';

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
		<div>
			<input
				type="search"
				name="search"
				placeholder="Пошук запчастини"
				class="w-1/3 min-w-2xs rounded-3xl border-none bg-white"
			/>
		</div>
	</section>

	<menu class="flex h-full flex-col gap-2 transition-all">
		<div class="h-full min-w-3xs overflow-auto">
			<Menu page={currentPage} />
		</div>
		<button type="button" class="btn preset-filled-primary-950-50" onclick={logout}>Logout</button>
	</menu>
	<section class="overflow-y-auto rounded-3xl border-[1.5rem] border-white bg-white">
		{@render children()}
	</section>
</main>
