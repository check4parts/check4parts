<script>
	let { data } = $props();
	let { price, warehouses, price_history, count } = $derived(data);
</script>

<div class="border-primary-950 overflow-hidden rounded-xl border-2">
	<div class="border-primary-950 p-4">
		<div class="grid grid-cols-2 gap-4">
			<div>
				<h3 class="text-primary-950 text-lg font-bold">Деталі імпорту прайсу</h3>
				<div class="mt-2 space-y-1">
					<p class="text-sm">
						<span class="text-primary-900 font-medium">Історичне ID:</span>
						<span class="font-mono">{price_history.id}</span>
					</p>
					{#if price_history.loaded_prices}
						<p class="text-sm">
							<span class="text-primary-900 font-medium">ID імпорту:</span>
							<span class="font-mono">{price_history.loaded_prices?.id}</span>
						</p>
						<p class="text-sm">
							<span class="text-primary-900 font-medium">HASH імпорту:</span>
							<span class="font-mono">{price_history.loaded_prices?.hash}</span>
						</p>
					{/if}
					<p class="text-sm">
						<span class="text-primary-900 font-medium">Дата:</span>
						{new Date(price_history.created_at).toLocaleDateString('uk-UA', {
							year: 'numeric',
							month: '2-digit',
							day: '2-digit',
							hour: '2-digit',
							minute: '2-digit'
						})}
					</p>
					<p class="text-sm">
						<span class="text-primary-900 font-medium">Постачальник:</span>
						{price_history.providers?.name || 'Не вказано'}
						{#if price_history.providers?.short_name}
							<span class="ml-1 text-xs">({price_history.providers.short_name})</span>
						{/if}
					</p>
					{#if price_history.status === 'actual'}
						<p class="text-sm">
							<span class="text-primary-900 font-medium">Статус:</span>
							<span class="rounded-full bg-green-100 px-2 py-1 text-xs text-green-800">
								Актуальний
							</span>
						</p>
						<p class="text-sm">
							<span class="text-primary-900 font-medium">Кількість:</span>
							{count || 'Не вказано'} (Відображено: {price?.length})
						</p>
					{:else if price_history.status === 'deleted'}
						<p class="text-sm">
							<span class="text-primary-900 font-medium">Статус:</span>
							<span class="rounded-full bg-red-100 px-2 py-1 text-xs text-red-800"> Видалено </span>
						</p>
					{/if}
				</div>
			</div>
		</div>
	</div>
</div>

{#if price_history.status !== 'deleted'}
	<div class="border-primary-950 mt-5 overflow-hidden rounded-xl border-2">
		<div class="max-h-[55vh] overflow-y-auto">
			<table class="table min-w-full border-collapse">
				<thead class="bg-primary-950 sticky top-0 z-10">
					<tr class="text-primary-50">
						<th class="p-2">Бренд</th>
						<th class="p-2">Артикул</th>
						<th class="p-2">Опис</th>
						<th class="p-2">Ціна</th>
						{#each warehouses as warehouse}
							<th class="p-2">
								{warehouse.name}
								{#if warehouse.short_name}
									<span class="ml-1 text-xs">({warehouse.short_name})</span>
								{/if}
							</th>
						{/each}
					</tr>
				</thead>
				<tbody class="!divide-primary-950 !divide-y-2">
					{#each price as item (item.id)}
						<tr class="divide-primary-950 hover:bg-primary-50 group w-full divide-x-2">
							<td class="p-2 font-medium">{item.brand}</td>
							<td class="p-2 font-mono">{item.article}</td>
							<td class="p-2">{item.description}</td>
							<td class="p-2 font-medium">
								{new Intl.NumberFormat('uk-UA', {
									style: 'currency',
									currency: 'UAH',
									minimumFractionDigits: 2
								}).format(item.price)}
							</td>

							{#each warehouses as warehouse}
								<td class="p-2 text-center">
									{#if item.rests[warehouse.id] && item.rests[warehouse.id] !== '0'}
										<span class="rounded-full bg-green-100 px-2 py-1 text-xs text-green-800">
											{item.rests[warehouse.id]}
										</span>
									{:else}
										<span class="rounded-full bg-red-100 px-2 py-1 text-xs text-red-800"> 0 </span>
									{/if}
								</td>
							{/each}
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
{:else}
	<div class="p-4 text-center text-gray-500">
		<p>Парайс видалено</p>
	</div>
{/if}
