<script lang="ts">
	import SearchResultCard from '$lib/components/cards/search/SearchResultCard.svelte';

	const { data } = $props();

	const search_query = $derived(data.searchQuery);
</script>

<div class="container mx-auto p-4">
	<h1 class="mb-6 text-2xl font-bold">
		{#if search_query}
			Результати пошуку для: "{search_query}"
		{:else}
			Введіть запит для пошуку
		{/if}
	</h1>

	{#await data.parts then parts}
		{#if parts}
			{#if parts.length === 0 && search_query}
				<p class="text-center text-lg text-gray-600">
					За вашим запитом "{search_query}" нічого не знайдено.
				</p>
			{:else if parts.length === 0 && !search_query}
				<p class="text-center text-lg text-gray-600">
					Введіть щось у поле пошуку, щоб знайти запчастини.
				</p>
			{:else}
				<div class="grid gap-6">
					{#each parts as part (part.code)}
						{#await part.rests}
							<SearchResultCard {part} rests={[]} />
						{:then data}
							<SearchResultCard {part} rests={data.rests} />
						{:catch error}
						 	{JSON.stringify(error)}
						{/await}
					{/each}
				</div>
			{/if}
		{/if}
	{:catch error}
		<p class="text-center text-lg text-red-500">
			Помилка при завантаженні результатів: {error.message}
		</p>
	{/await}
</div>
