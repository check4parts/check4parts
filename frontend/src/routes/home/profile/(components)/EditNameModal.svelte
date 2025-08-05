<script lang="ts">
	import { enhance } from '$app/forms';
	import { Dialog } from 'bits-ui';
	import type { ActionData } from '../$types';
	import InputTextField from '$lib/components/inputs/modal/InputTextField.svelte';

	interface Props {
		openState: boolean;
		modalClose?: () => void;
		data: {
			first_name: string;
			last_name: string;
			middle_name: string;
		};
		form?: ActionData;
		id: string;
	}

	let {
		openState = $bindable(false),
		modalClose = () => {
			openState = false;
		},
		form = $bindable(),
		data,
		id
	}: Props = $props();

	let loading = $state(false);

	$effect(() => {
		loading = false;
	});
</script>

<Dialog.Root bind:open={openState}>
	<Dialog.Portal>
		<Dialog.Overlay
			class="data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 fixed inset-0 z-50 bg-black/80"
		/>
		<Dialog.Content
			class="fixed left-[50%] top-[50%] z-50 h-fit w-1/2 translate-x-[-50%] translate-y-[-50%] rounded-xl bg-white p-4"
		>
			<div class="flex w-full justify-end">
				<button type="button" class="preset-tonal-surface-100" onclick={modalClose}>
					<img src="/close-icon.svg" alt="close" class="size-4" />
				</button>
			</div>
			<Dialog.Title
				class="з-4 flex w-full items-center justify-end text-lg font-semibold tracking-tight"
			>
				<h4 class="h5 w-full text-center">Редагування ПІБ</h4>
			</Dialog.Title>
			<Dialog.Description class="p-4">
				<form
					class="flex flex-col gap-5 px-10"
					method="POST"
					use:enhance={() => {
						return async ({ update }) => {
							update({ reset: false });
						};
					}}
					action="?/editName"
					onsubmit={() => (loading = true)}
				>
					<input type="hidden" name="id" value={id} />
					<InputTextField
						lable="Прізвище"
						placeholder="Введіть прізвище"
						name="last_name"
						value={data.last_name}
					/>
					<InputTextField
						lable="Ім'я"
						placeholder="Введіть ім'я"
						name="first_name"
						value={data.first_name}
					/>
					<InputTextField
						lable="По батькові"
						placeholder="Введіть по батькові"
						name="middle_name"
						value={data.middle_name}
					/>

					<div class="flex justify-end gap-4">
						<button
							type="button"
							class="btn preset-outlined-primary-950-50 text-xl"
							onclick={modalClose}>Скасувати</button
						>
						<button
							type="submit"
							class="btn preset-filled-primary-950-50 text-xl"
							disabled={loading}
							>{#if loading}
								Завантаження...
							{:else}
								Зберегти
							{/if}</button
						>
					</div>
				</form>
			</Dialog.Description>
			<Dialog.Close />
		</Dialog.Content>
	</Dialog.Portal>
</Dialog.Root>
