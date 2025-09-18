<script lang="ts">
	import { goto, preloadData } from '$app/navigation';

	let { data } = $props();
	let { suppliers } = $derived(data);
</script>

{#snippet noSuppliersMessage()}
	<div class="flex h-full w-full flex-col items-center justify-center">
		<h3 class="h5">Тут поки що порожньо.</h3>
		<p>Додайте першого постачальника, щоб почати.</p>
	</div>
{/snippet}

<section class="flex flex-col gap-4 overflow-auto">
	<div>
		<a
			href="/home/settings/suppliers/api/add"
			class="btn preset-tonal-success font-bold"
		>
			<i class="fas fa-plus"></i>
			Підключити постачальника по API
		</a>
	</div>
	{#if suppliers.length > 0}
		<div class="border-primary-950 overflow-hidden rounded-xl border-2">
			<div class="max-h-full overflow-y-auto">
				<table class="table min-w-full border-collapse">
					<thead class="bg-primary-950 sticky top-0 z-10">
						<tr class="text-primary-50">
							<th class="w-1/2">Назва</th>
							<th class="w-1/2">Доступ</th>
						</tr>
					</thead>
					<tbody class="!divide-primary-950 !divide-y-2">
						{#each suppliers as supplier (supplier.id)}
							<tr
								onmousemove={() => preloadData('/home/settings/suppliers/api/' + supplier.id)}
								onclick={() => goto('/home/settings/suppliers/api/' + supplier.id)}
								class="divide-primary-950 hover:bg-primary-50 group w-full divide-x-2"
								class:bg-amber-100={supplier.state === 'paused'}
							>
								<td>{supplier.providers.name}</td>
								<td class="flex gap-5">
									{#if supplier.access_data}
										{#each supplier.providers.access_props as prop}
											{#if prop.type === 'password'}
												<p>{prop.title}: (приховано)</p>
											{:else}
												<p>{prop.title}: {supplier.access_data[prop.name]}</p>
											{/if}
										{/each}
									{:else}
										<p>Немає доступу</p>
									{/if}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	{:else}
		{@render noSuppliersMessage()}
	{/if}
</section>
