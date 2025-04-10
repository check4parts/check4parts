import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ depends, locals: { supabase } }) => {
	depends('supabase:db:trading-points');
	const { data: points } = await supabase.from('trading_points').select('*').order('name');
	return { points: points ?? [] };
};

export const actions: Actions = {
	addTradingPoint: async ({ request, locals: { supabase } }) => {
		const formData = await request.formData();

		const name = formData.get('name');
		const region = formData.get('region');
		const locality = formData.get('locality');
		const street = formData.get('street');

		let { data, error } = await supabase.from('trading_points').select('*').eq('name', name);

		if (error) {
			return { success: false, message: error.message };
		} else if (data!.length > 0) {
			return {
				success: false,
				id: 0,
				message: 'name_already_exists'
			};
		}

		let { data: insertData, error: insertError } = await supabase
			.from('trading_points')
			.insert([{ name, region, locality, street }])
			.select();

		if (insertError) {
			return {
				success: false,
				id: 0,
				message: insertError.message
			};
		} else {
			return { success: true, id: 0 };
		}
	},
	editTradingPoint: async ({ request, locals: { supabase } }) => {
		const formData = await request.formData();

		const id = formData.get('id');
		const name = formData.get('name');
		const region = formData.get('region');
		const locality = formData.get('locality');
		const street = formData.get('street');

		let { data, error } = await supabase.from('trading_points').select('*').eq('name', name);

		console.log(data);

		if (error) {
			return { success: false, message: error.message };
		} else if (data!.length > 0 && data![0].id != id) {
			return {
				success: false,
				message: 'name_already_exists',
				id
			};
		}

		const { error: editError } = await supabase
			.from('trading_points')
			.update({ name, region, locality, street })
			.eq('id', id)
			.select();

		if (error) {
			return { success: false, message: editError?.message, id };
		} else {
			return { success: true, id };
		}
	},
	delete: async ({ request, locals: { supabase } }) => {
		const formData = await request.formData();
		const id = formData.get('id');
		const { error } = await supabase.from('trading_points').delete().eq('id', id);
		if (error) {
			return { success: false, message: error.message };
		} else {
			return { success: true, message: 'deleted' };
		}
	}
};
