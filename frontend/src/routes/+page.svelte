<script lang="ts">
	import Advantages from '$lib/landing/Advantages.svelte';
	import Audience from '$lib/landing/Audience.svelte';
	import ContactForm from '$lib/landing/ContactForm.svelte';
	import Functions from '$lib/landing/Functions.svelte';
	import Hero from '$lib/landing/Hero.svelte';

	let { data, form } = $props();
	let { user } = $derived(data);
</script>

<svelte:head>
	<title>CHECK4PARTS</title>
</svelte:head>

<main class="bg-surface-50 overflow-hidden bg-[url(/hero-vector.svg)] bg-top bg-no-repeat pt-10">
	<header class="container mx-auto mb-10 flex items-center justify-between px-2">
		<h1 class="h3">CHECK<span class="text-primary-600">4PARTS</span></h1>

		<nav class="hidden lg:block">
			<ul class="flex items-center gap-20">
				<li><a href="#hero">Головна</a></li>
				<li><a href="#functions">Функції</a></li>
				<li><a href="#audience">Користувачі</a></li>
				<li><a href="#advantages">Переваги</a></li>
				<li><a href="#contacts">Контакти</a></li>
			</ul>
		</nav>
		{#if user}
			<a href="/home" class="btn preset-filled-primary-950-50 px-20 font-bold"> Увійти </a>
		{:else}
			<a href="#contacts" class="btn preset-filled-primary-950-50 font-bold"> Зв'язатися </a>
		{/if}
	</header>
	<section id="hero" class="mt-15">
		<Hero />
	</section>
	<section id="functions" class="mt-20">
		<Functions />
	</section>
	<section id="audience" class="pt-35 from-primary-500/10 to-surface-50 bg-gradient-to-t">
		<Audience />
	</section>
	<section
		id="advantages"
		class="pt-35 from-primary-500/10 to-surface-50 before:text-surface-50 bg-gradient-to-b"
	>
		<Advantages />
	</section>
	<section id="contacts" class="mt-20">
		<ContactForm {form} />
	</section>
	<footer class="sm:bg-primary-950 bg-surface-50 mx-auto py-3">
		<p class="sm:text-surface-50 text-primary-950 container mx-auto text-left">© 2025 Check4parts Landing Page.</p>
	</footer>
</main>
