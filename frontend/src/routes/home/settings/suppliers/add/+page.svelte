<script lang="ts">
	import AddKeyModal from './(components)/AddKeyModal.svelte';

	let { data } = $props();
	let { suppliers, added_suppliers } = $derived(data);
</script>

<header class="flex items-center justify-between">
	<h2 class="h4">Додати постачальника</h2>
</header>

<section class="m-5 flex flex-wrap items-center gap-5">
	{#each suppliers as supplier (supplier.id)}
		<AddKeyModal
			title="Додавання постачальника '{supplier.name}'"
			supplier_id={supplier.id}
			form_structure={supplier.access_props}
			data_props={supplier.data_props}
		>
			<div
				class="hover:outline-primary-50 cursor-pointer rounded-2xl outline-offset-2 hover:outline-2"
			>
				<img src={supplier.logo_url} alt={supplier.name} />
			</div>
		</AddKeyModal>
	{/each}
</section>
