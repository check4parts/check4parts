import { fail } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';

export const load: PageServerLoad = async ({ depends, locals: { supabase } }) => {
	depends('supabase:db:client_types');
	const { data: types } = await supabase.from('client_types').select('*').order('name');

	return { types: types ?? [] };
};

export const actions: Actions = {
	add: async ({ request, locals: { supabase } }) => {
		const form_data = await request.formData();

		const first_name = form_data.get('first_name')?.toString();
		const last_name = form_data.get('last_name')?.toString();
		const middle_name = form_data.get('middle_name')?.toString();
		const phone_number = form_data.get('phone_number')?.toString();
		const address = form_data.get('address')?.toString();
		const note = form_data.get('note')?.toString();
		const type_id = form_data.get('client_type')?.toString();

		if (!first_name || !phone_number || !type_id) {
			return fail(400, { missing: true });
		}

		const clientData = {
			first_name,
			last_name,
			middle_name,
			phone_number,
			address,
			note,
			type_id
		};

		// Парсинг автомобілів з форми
		const cars: { [key: string]: string }[] = [];
		for (const [key, value] of form_data.entries()) {
			const match = key.match(/cars\[(\d+)\]\[(\w+)\]/);
			if (match) {
				const index = parseInt(match[1]);
				const field = match[2];

				if (!cars[index]) {
					cars[index] = {};
				}
				cars[index][field] = value.toString();
			}
		}

		const { data, error } = await supabase
			.from('clients')
			.insert(clientData)
			.select('*')
			.single();

		if (error) {
			console.error('Client insert error:', error);
			return fail(500, { error: error.code });
		}

		if (!data?.id) {
			return fail(500, { error: 'Failed to retrieve client ID' });
		}

		const client_id = data.id;

		for (const car of cars) {
			const carData = {
				client_id,
				name: car['name'] || null,
				vin_code: car['vinCode'] || null,
				license_plate: car['plate'] || null
			};

			const { error: carError } = await supabase
				.from('cars')
				.insert(carData);

			if (carError) {
				console.error('Car insert error:', carError);
				return fail(500, { error: carError.code });
			}
		}

		return {
			success: true,
			id: data.id,
			first_name: data.first_name,
			last_name: data.last_name,
			middle_name: data.middle_name,
			phone_number: data.phone_number,
			address: data.address,
			note: data.note,
			type_id: data.type_id
		};
	}
};
