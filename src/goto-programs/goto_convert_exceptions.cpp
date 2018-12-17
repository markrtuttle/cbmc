/*******************************************************************\

Module: Program Transformation

Author: Daniel Kroening, kroening@kroening.com

\*******************************************************************/

/// \file
/// Program Transformation

#include "goto_convert_class.h"

#include <util/std_expr.h>

void goto_convertt::convert_msc_try_finally(
  const codet &code,
  goto_programt &dest,
  const irep_idt &mode)
{
  INVARIANT_WITH_DIAGNOSTICS(
    code.operands().size() == 2,
    "msc_try_finally expects two arguments",
    code.find_source_location());

  goto_programt tmp;
  tmp.add_instruction(SKIP)->source_location=code.source_location();

  {
    // save 'leave' target
    leave_targett leave_target(targets);
    targets.set_leave(tmp.instructions.begin());

    // first put 'finally' code onto destructor stack
    node_indext old_stack_top = targets.destructor_stack.get_current_node();
    targets.destructor_stack.add(to_code(code.op1()));

    // do 'try' code
    convert(to_code(code.op0()), dest, mode);

    // pop 'finally' from destructor stack
    targets.destructor_stack.set_current_node(old_stack_top);

    // 'leave' target gets restored here
  }

  // now add 'finally' code
  convert(to_code(code.op1()), dest, mode);

  // this is the target for 'leave'
  dest.destructive_append(tmp);
}

void goto_convertt::convert_msc_try_except(
  const codet &code,
  goto_programt &dest,
  const irep_idt &mode)
{
  INVARIANT_WITH_DIAGNOSTICS(
    code.operands().size() == 3,
    "msc_try_except expects three arguments",
    code.find_source_location());

  convert(to_code(code.op0()), dest, mode);

  // todo: generate exception tracking
}

void goto_convertt::convert_msc_leave(
  const codet &code,
  goto_programt &dest,
  const irep_idt &mode)
{
  INVARIANT_WITH_DIAGNOSTICS(
    targets.leave_set, "leave without target", code.find_source_location());

  // need to process destructor stack
  unwind_destructor_stack(
    code.source_location(), dest, mode, targets.leave_stack_node);

  dest.add(
    goto_programt::make_goto(targets.leave_target, code.source_location()));
}

void goto_convertt::convert_try_catch(
  const codet &code,
  goto_programt &dest,
  const irep_idt &mode)
{
  INVARIANT_WITH_DIAGNOSTICS(
    code.operands().size() >= 2,
    "try_catch expects at least two arguments",
    code.find_source_location());

  // add the CATCH-push instruction to 'dest'
  goto_programt::targett catch_push_instruction=dest.add_instruction();
  catch_push_instruction->make_catch();
  catch_push_instruction->source_location=code.source_location();

  code_push_catcht push_catch_code;

  // the CATCH-push instruction is annotated with a list of IDs,
  // one per target
  code_push_catcht::exception_listt &exception_list=
    push_catch_code.exception_list();

  // add a SKIP target for the end of everything
  goto_programt end;
  goto_programt::targett end_target = end.add(goto_programt::make_skip());

  // the first operand is the 'try' block
  convert(to_code(code.op0()), dest, mode);

  // add the CATCH-pop to the end of the 'try' block
  goto_programt::targett catch_pop_instruction=dest.add_instruction();
  catch_pop_instruction->make_catch();
  catch_pop_instruction->code=code_pop_catcht();

  // add a goto to the end of the 'try' block
  dest.add(goto_programt::make_goto(end_target));

  for(std::size_t i=1; i<code.operands().size(); i++)
  {
    const codet &block=to_code(code.operands()[i]);

    // grab the ID and add to CATCH instruction
    exception_list.push_back(
      code_push_catcht::exception_list_entryt(block.get(ID_exception_id)));

    goto_programt tmp;
    convert(block, tmp, mode);
    catch_push_instruction->targets.push_back(tmp.instructions.begin());
    dest.destructive_append(tmp);

    // add a goto to the end of the 'catch' block
    dest.add(goto_programt::make_goto(end_target));
  }

  catch_push_instruction->code=push_catch_code;

  // add the end-target
  dest.destructive_append(end);
}

void goto_convertt::convert_CPROVER_try_catch(
  const codet &code,
  goto_programt &dest,
  const irep_idt &mode)
{
  INVARIANT_WITH_DIAGNOSTICS(
    code.operands().size() == 2,
    "CPROVER_try_catch expects two arguments",
    code.find_source_location());

  // this is where we go after 'throw'
  goto_programt tmp;
  tmp.add_instruction(SKIP)->source_location=code.source_location();

  // set 'throw' target
  throw_targett throw_target(targets);
  targets.set_throw(tmp.instructions.begin());

  // now put 'catch' code onto destructor stack
  code_ifthenelset catch_code(exception_flag(mode), to_code(code.op1()));
  catch_code.add_source_location()=code.source_location();

  // Store the point before the temp catch code.
  node_indext old_stack_top = targets.destructor_stack.get_current_node();
  targets.destructor_stack.add(catch_code);

  // now convert 'try' code
  convert(to_code(code.op0()), dest, mode);

  // pop 'catch' code off stack
  targets.destructor_stack.set_current_node(old_stack_top);

  // add 'throw' target
  dest.destructive_append(tmp);
}

void goto_convertt::convert_CPROVER_throw(
  const codet &code,
  goto_programt &dest,
  const irep_idt &mode)
{
  // set the 'exception' flag
  {
    goto_programt::targett t_set_exception=
      dest.add_instruction(ASSIGN);

    t_set_exception->source_location=code.source_location();
    t_set_exception->code = code_assignt(exception_flag(mode), true_exprt());
  }

  // do we catch locally?
  if(targets.throw_set)
  {
    // need to process destructor stack
    unwind_destructor_stack(
      code.source_location(), dest, mode, targets.throw_stack_node);

    // add goto
    dest.add(
      goto_programt::make_goto(targets.throw_target, code.source_location()));
  }
  else // otherwise, we do a return
  {
    // need to process destructor stack
    unwind_destructor_stack(code.source_location(), dest, mode);

    // add goto
    dest.add(
      goto_programt::make_goto(targets.return_target, code.source_location()));
  }
}

void goto_convertt::convert_CPROVER_try_finally(
  const codet &code,
  goto_programt &dest,
  const irep_idt &mode)
{
  INVARIANT_WITH_DIAGNOSTICS(
    code.operands().size() == 2,
    "CPROVER_try_finally expects two arguments",
    code.find_source_location());

  // first put 'finally' code onto destructor stack
  node_indext old_stack_top = targets.destructor_stack.get_current_node();
  targets.destructor_stack.add(to_code(code.op1()));

  // do 'try' code
  convert(to_code(code.op0()), dest, mode);

  // pop 'finally' from destructor stack
  targets.destructor_stack.set_current_node(old_stack_top);

  // now add 'finally' code
  convert(to_code(code.op1()), dest, mode);
}

symbol_exprt goto_convertt::exception_flag(const irep_idt &mode)
{
  irep_idt id="$exception_flag";

  symbol_tablet::symbolst::const_iterator s_it=
    symbol_table.symbols.find(id);

  if(s_it==symbol_table.symbols.end())
  {
    symbolt new_symbol;
    new_symbol.base_name="$exception_flag";
    new_symbol.name=id;
    new_symbol.is_lvalue=true;
    new_symbol.is_thread_local=true;
    new_symbol.is_file_local=false;
    new_symbol.type=bool_typet();
    new_symbol.mode = mode;
    symbol_table.insert(std::move(new_symbol));
  }

  return symbol_exprt(id, bool_typet());
}

/// Unwinds the destructor stack and creates destructors for each node between
/// destructor_start_point and destructor_end_point (including the start,
/// excluding the end).
///
/// If destructor_end_point isn't passed, it will unwind the whole stack.
/// If destructor_start_point isn't passed, it will unwind from the current
/// node.
bool goto_convertt::unwind_destructor_stack(
  const source_locationt &source_location,
  goto_programt &dest,
  const irep_idt &mode,
  optionalt<node_indext> destructor_end_point,
  optionalt<node_indext> destructor_start_point)
{
  return unwind_destructor_stack(
    source_location,
    dest,
    targets.destructor_stack,
    mode,
    destructor_end_point,
    destructor_start_point);
}

bool goto_convertt::unwind_destructor_stack(
  const source_locationt &source_location,
  goto_programt &dest,
  destructor_treet &destructor_stack,
  const irep_idt &mode,
  optionalt<node_indext> destructor_end_point,
  optionalt<node_indext> destructor_start_point)
{
  std::vector<codet> stack = destructor_stack.get_destructors(
    destructor_end_point, destructor_start_point);

  for(const codet &destructor : stack)
  {
    // Copy, assign source location then convert.
    codet d_code = destructor;
    d_code.add_source_location() = source_location;
    convert(d_code, dest, mode);
  }

  return !stack.empty();
}
