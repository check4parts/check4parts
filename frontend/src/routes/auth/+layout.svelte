<script>
	let { children } = $props();
</script>

<main class="grid h-screen w-screen grid-cols-[0_1fr] gap-0.5 lg:grid-cols-2">
	<section class="bg-[url(/background_auth.png)]"></section>
	<section class="flex flex-col bg-white align-middle">
		{@render children()}
	</section>
</main>
