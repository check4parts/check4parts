<script lang="ts">
	import InputRadioButtons from '$lib/components/inputs/card/InputRadioButtons.svelte';

	let { types }: { types: { id: string; name: string }[] } = $props();
</script>

<div class="card preset-filled-surface-50-950 flex flex-col p-8">
	<h3 class="h6 mb-5">Тип клієнта</h3>
	<InputRadioButtons
		name="client_type"
		required
		items={types.map((t) => {
			return {
				value: t.id,
				label: t.name
			};
		})}
	/>
</div>
