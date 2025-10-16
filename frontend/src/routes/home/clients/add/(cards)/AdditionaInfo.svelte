<script>
	import InputTextareaField from '$lib/components/inputs/card/InputTextareaField.svelte';
	import InputTextField from '$lib/components/inputs/card/InputTextField.svelte';

	let { missing = false } = $props();
</script>

<div class="card preset-filled-surface-50-950 flex flex-col p-8">
	<h3 class="h6">Додаткова інформація</h3>
	<div class="flex flex-col gap-10">
		<InputTextField
			lable="Націнка"
			placeholder="Вкажіть відсоток націнки"
			name="markup"
			{missing}
		/>
		<InputTextField
			lable="Адреса доставки"
			name="address"
			placeholder="Введіть адресу доставки"
			{missing}
		/>
		<InputTextareaField
			lable="Примітка"
			name="note"
			placeholder="Додайте інформацію або коментар"
			{missing}
		/>
	</div>
</div>
