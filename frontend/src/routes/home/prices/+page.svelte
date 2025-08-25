<script lang="ts">
	let { data } = $props();
	let { price_history, staff } = data;
</script>

{#snippet priceHistoryTable(price_history: any[])}
	<div class="border-primary-950 overflow-hidden rounded-xl border-2">
		<div class="max-h-[79vh] overflow-y-auto">
			<table class="table min-w-full border-collapse">
				<thead class="bg-primary-950 sticky top-0 z-10">
					<tr class="text-primary-50">
						<th>ID</th>
						<th>Дата створення</th>
						<th>Користувач</th>
						<th>Постачальник</th>
						<th>Хеш</th>
						<th>Статус</th>
					</tr>
				</thead>
				<tbody class="!divide-primary-950 !divide-y-2">
					{#each price_history as entry (entry.id)}
						<tr class="divide-primary-950 hover:bg-primary-50 group w-full divide-x-2">
							<td class="p-2">
								{#if entry.status === 'actual' || entry.status === 'deleted' || entry.status === 'cloned'}
									<a
										href={`/home/prices/${entry.id}`}
										class="font-medium text-blue-600 hover:text-blue-800"
									>
										{entry.id}
									</a>
								{:else}
									{entry.id}
								{/if}
							</td>
							<td class="p-2">
								{new Date(entry.created_at).toLocaleDateString('uk-UA', {
									year: 'numeric',
									month: '2-digit',
									day: '2-digit',
									hour: '2-digit',
									minute: '2-digit'
								})}
							</td>
							<td class="p-2">
								{#await staff}
									Хтось...
								{:then staff}
									{staff.find((employee) => employee.user_id === entry.user_id)?.last_name || ''}
									{staff.find((employee) => employee.user_id === entry.user_id)?.first_name || ''}
								{/await}
							</td>
							<td class="p-2">{entry.providers?.name || '—'}</td>

							<td class="p-2">{(entry.loaded_prices?.hash || '—').slice(0, 8)}</td>
							<td class="p-2">
								{#if entry.status === 'uploading'}
									<span class="rounded-full bg-yellow-100 px-2 py-1 text-xs text-yellow-800">
										Завантаження
									</span>
								{:else if entry.status === 'deleted'}
									<span class="rounded-full bg-red-100 px-2 py-1 text-xs text-red-800">
										Видалено
									</span>
								{:else if entry.status === 'actual'}
									<span class="rounded-full bg-green-100 px-2 py-1 text-xs text-green-800">
										Актуальний
									</span>
								{:else if entry.status === 'cloned'}
									<span class="rounded-full bg-green-100 px-2 py-1 text-xs text-green-800">
										Клонований
									</span>
								{:else}
									<span class="rounded-full bg-gray-100 px-2 py-1 text-xs text-gray-800">
										Невідомо
									</span>
								{/if}
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
{/snippet}

<header class="flex items-center justify-between">
	<h2 class="h3">Історія завантажень</h2>
</header>

<section class="mt-4">
	{#await price_history}
		<p class="text-center text-gray-500">Завантаження історії цін...</p>
	{:then price_history}
		{#if price_history.length === 0}
			<p class="text-center text-gray-500">Історія цін порожня.</p>
		{:else}
			{@render priceHistoryTable(price_history)}
		{/if}
	{:catch error}
		<p class="text-center text-red-500">Помилка завантаження історії цін: {error.message}</p>
	{/await}
</section>
