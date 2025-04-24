<script lang="ts">
	import { Dialog } from 'bits-ui';
	import type { Snippet } from 'svelte';
	import InputTextField from '$lib/components/modal-form/InputTextField.svelte';
	import InputPasswordField from '$lib/components/modal-form/InputPasswordField.svelte';

	interface FormStructureItem {
		name: string;
		title: string;
		type: string;
		placeholder: string;
	}

	interface Props {
		open?: boolean;
		modalClose?: () => void;
		title: string;
		supplier_id: string;
		form_structure: FormStructureItem[];
		children: Snippet;
		data_props: Object;
	}

	let {
		open = $bindable(false),
		modalClose = () => {
			open = false;
		},
		title,
		supplier_id,
		form_structure,
		children,
		data_props
	}: Props = $props();
</script>

<Dialog.Root bind:open>
	<Dialog.Trigger class="rounded-2xl">
		{@render children()}
	</Dialog.Trigger>
	<Dialog.Portal>
		<Dialog.Overlay
			class="data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 fixed inset-0 z-50 bg-black/80"
		/>
		<Dialog.Content
			class="fixed top-[50%] left-[50%] z-50 w-1/3 translate-x-[-50%] translate-y-[-50%] rounded-xl bg-white p-4"
		>
			<div class="absolute top-3 right-4">
				<button type="button" class="preset-tonal-surface-100" onclick={modalClose}>
					<img src="/close-icon.svg" alt="close" class="size-4" />
				</button>
			</div>
			<Dialog.Title
				class="flex w-full items-center justify-end p-4 text-lg font-semibold tracking-tight"
			>
				<h4 class="h5 w-full text-center">
					{title}
				</h4>
			</Dialog.Title>
			<Dialog.Description>
				<form method="post" action="?/add">
					<input type="hidden" name="data_props" value={JSON.stringify(data_props)} />
					<input type="hidden" name="supplier_id" value={supplier_id} />
					{#each form_structure as item}
						{#if item.type === 'text'}
							<InputTextField
								lable={item.title}
								name={item.name}
								placeholder={item.placeholder}
								required
							/>
						{:else if item.type === 'password'}
							<InputPasswordField
								lable={item.title}
								name={item.name}
								placeholder={item.placeholder}
								required
							/>
						{/if}
					{/each}

					<div class="mt-5 flex h-fit items-center justify-end gap-3">
						<button
							type="button"
							class="btn btn-lg preset-outlined-primary-950-50"
							onclick={modalClose}
						>
							Скасувати
						</button>
						<button type="submit" class="btn btn-lg preset-filled-primary-950-50"> Додати </button>
					</div>
				</form>
			</Dialog.Description>
		</Dialog.Content>
	</Dialog.Portal>
</Dialog.Root>
