import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ depends, locals: { supabase } }) => {
  depends('supabase:db:roles');
  const { data: roles } = await supabase
    .from('roles')
    .select('*')
    .order('name');

  depends('supabase:db:trading-points');
  const { data: points } = await supabase.from('trading_points').select('*').order('name');
  
  return { roles: roles ?? [], points: points ?? [] };
};
