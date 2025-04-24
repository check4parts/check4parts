<script lang="ts">
	import { goto, preloadData } from '$app/navigation';

	let { data } = $props();
	let { suppliers } = $derived(data);
	$inspect(suppliers);
</script>

{#snippet noSuppliersMessage()}
	<div class="flex h-full w-full flex-col items-center justify-center">
		<h3 class="h5">Тут поки що порожньо.</h3>
		<p>Додайте першого постачальника, щоб почати .</p>
	</div>
{/snippet}

<header class="flex items-center justify-between">
	<h2 class="h3">Постачальники</h2>
	<a class="btn preset-filled-primary-950-50" href="/home/settings/suppliers/add"
		>Додати постачальника</a
	>
</header>

{#if suppliers.length > 0}
	<section class="mt-10 flex flex-col gap-4">
		<div class="border-primary-950 overflow-hidden rounded-xl border-2">
			<div class="max-h-[70vh] overflow-y-auto">
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
								onmousemove={() => preloadData('/home/settings/suppliers/' + supplier.id)}
								onclick={() => goto('/home/settings/suppliers/' + supplier.id)}
								class="divide-primary-950 group hover:bg-primary-50 w-full divide-x-2"
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
	</section>
{:else}
	<section class="h-2/3">
		{@render noSuppliersMessage()}
	</section>
{/if}
